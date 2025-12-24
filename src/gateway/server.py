# src/gateway/server.py
from flask import Flask, request, jsonify
import redis
import json
import uuid
import os
import sys
from datetime import datetime
import signal
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Import metrics
try:
    from shared.metrics import (
        task_submissions, task_completions, task_failures,
        active_workers, pending_tasks, tasks_in_dlq
    )
except ImportError:
    # Fallback if metrics module not available
    print("[Gateway] Warning: Could not import metrics module")
    pass

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
PORT = int(os.getenv('PORT', 5000))
GATEWAY_ID = f"gateway-{str(uuid.uuid4())[:8]}"

# Redis clients
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    retry_on_timeout=True
)

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint"""
    try:
        # Get system metrics
        workers = redis_client.smembers('workers:active')
        queue_length = redis_client.llen('tasks:pending')
        completed = redis_client.get('tasks:completed') or 0
        
        # Update Prometheus gauges
        active_workers.set(len(workers))
        pending_tasks.labels(priority='normal').set(redis_client.llen('tasks:pending'))
        pending_tasks.labels(priority='high').set(redis_client.llen('tasks:pending:high'))
        tasks_in_dlq.set(redis_client.llen('dlq:failed_tasks'))
        
        return jsonify({
            'status': 'healthy',
            'gateway': GATEWAY_ID,
            'workers': len(workers),
            'pending_tasks': queue_length,
            'completed_tasks': int(completed),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except redis.RedisError as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/tasks', methods=['POST'])
def submit_task():
    """Submit a new task"""
    try:
        data = request.get_json()
        
        if not data or 'type' not in data or 'data' not in data:
            return jsonify({'error': 'Type and data are required'}), 400
        
        task_id = str(uuid.uuid4())
        priority = data.get('priority', 'normal')
        
        task = {
            'id': task_id,
            'type': data['type'],
            'data': data['data'],
            'priority': priority,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'submitted_by': GATEWAY_ID
        }
        
        # Store task metadata
        redis_client.set(f'task:{task_id}', json.dumps(task))
        
        # Add to appropriate queue
        queue_key = 'tasks:pending:high' if priority == 'high' else 'tasks:pending'
        redis_client.lpush(queue_key, task_id)
        
        # Publish notification to workers
        redis_client.publish('tasks:new', json.dumps({
            'task_id': task_id,
            'priority': priority
        }))
        
        # Record metrics
        task_submissions.labels(priority=priority, task_type=data['type']).inc()
        
        print(f"[Gateway] 📤 SUBMITTED task {task_id} | Type: {data['type']} | Priority: {priority}")
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Task submitted successfully'
        }), 201
        
    except Exception as e:
        print(f"[Gateway] Error submitting task: {e}")
        return jsonify({'error': 'Failed to submit task'}), 500

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get task status"""
    try:
        task_data = redis_client.get(f'task:{task_id}')
        
        if not task_data:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify(json.loads(task_data)), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve task'}), 500

@app.route('/tasks', methods=['GET'])
def list_tasks():
    """List all tasks"""
    try:
        status_filter = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        # Get all task keys
        keys = redis_client.keys('task:*')
        tasks = []
        
        for key in keys[:limit]:
            task_data = redis_client.get(key)
            if task_data:
                task = json.loads(task_data)
                if not status_filter or task['status'] == status_filter:
                    tasks.append(task)
        
        return jsonify({
            'tasks': tasks,
            'count': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list tasks'}), 500

@app.route('/workers', methods=['GET'])
def list_workers():
    """List active workers"""
    try:
        worker_ids = redis_client.smembers('workers:active')
        workers = []
        
        for worker_id in worker_ids:
            worker_data = redis_client.get(f'worker:{worker_id}')
            if worker_data:
                workers.append(json.loads(worker_data))
        
        return jsonify({
            'workers': workers,
            'count': len(workers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list workers'}), 500

@app.route('/dlq/failed-tasks', methods=['GET'])
def get_dlq_failed_tasks():
    """Get all tasks in the dead letter queue"""
    try:
        dlq_size = redis_client.llen('dlq:failed_tasks')
        
        # Get DLQ task IDs (limit to last 100)
        task_ids = redis_client.lrange('dlq:failed_tasks', 0, 99)
        
        failed_tasks = []
        for task_id in task_ids:
            task_data = redis_client.get(f'task:{task_id}')
            if task_data:
                task = json.loads(task_data)
                failed_tasks.append(task)
        
        return jsonify({
            'total': dlq_size,
            'tasks': failed_tasks,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get DLQ: {str(e)}'}), 500

@app.route('/dlq/failed-tasks/<task_id>', methods=['DELETE'])
def remove_from_dlq(task_id):
    """Remove a task from the dead letter queue"""
    try:
        redis_client.lrem('dlq:failed_tasks', 0, task_id)
        return jsonify({'success': True, 'message': f'Task {task_id} removed from DLQ'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to remove from DLQ: {str(e)}'}), 500

@app.route('/dlq/failed-tasks/<task_id>/retry', methods=['POST'])
def retry_dlq_task(task_id):
    """Retry a task from the dead letter queue"""
    try:
        task_data = redis_client.get(f'task:{task_id}')
        if not task_data:
            return jsonify({'error': 'Task not found'}), 404
        
        task = json.loads(task_data)
        
        # Reset retry count to allow retries
        task['retry_count'] = 0
        task['status'] = 'pending'
        task['last_error_at'] = None
        
        redis_client.set(f'task:{task_id}', json.dumps(task))
        
        # Move back to pending queue
        queue_key = 'tasks:pending:high' if task.get('priority') == 'high' else 'tasks:pending'
        redis_client.lpush(queue_key, task_id)
        
        # Remove from DLQ
        redis_client.lrem('dlq:failed_tasks', 0, task_id)
        
        # Notify workers
        redis_client.publish('tasks:new', json.dumps({
            'task_id': task_id,
            'priority': task.get('priority', 'normal')
        }))
        
        return jsonify({'success': True, 'message': f'Task {task_id} moved back to queue'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retry task: {str(e)}'}), 500

def signal_handler(sig, frame):
    """Graceful shutdown"""
    print(f"\n[Gateway] Shutting down gracefully...")
    redis_client.close()
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"[Gateway] Server {GATEWAY_ID} starting on port {PORT}")
    print(f"[Gateway] Health check: http://localhost:{PORT}/health")
    print(f"[Gateway] Redis: {REDIS_HOST}:{REDIS_PORT}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=PORT, debug=False)