# src/dashboard/app.py
"""
Web dashboard for the distributed task queue system
"""

from flask import Flask, render_template, jsonify
import redis
import json
import os
from datetime import datetime
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__, static_folder='static', template_folder='templates')

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=5
)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        # Get worker info
        workers = redis_client.smembers('workers:active')
        worker_details = []
        
        for worker_id in workers:
            worker_data = redis_client.get(f'worker:{worker_id}')
            if worker_data:
                worker = json.loads(worker_data)
                worker_details.append(worker)
        
        # Get queue stats
        pending_normal = redis_client.llen('tasks:pending')
        pending_high = redis_client.llen('tasks:pending:high')
        retry_count = redis_client.zcard('tasks:retry')
        dlq_count = redis_client.llen('dlq:failed_tasks')
        completed = int(redis_client.get('tasks:completed') or 0)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'workers': {
                'active': len(workers),
                'details': worker_details
            },
            'queues': {
                'pending_normal': pending_normal,
                'pending_high': pending_high,
                'retry': retry_count,
                'dlq': dlq_count
            },
            'tasks': {
                'completed': completed,
                'pending': pending_normal + pending_high,
                'retrying': retry_count,
                'failed': dlq_count
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/recent')
def get_recent_tasks():
    """Get recent tasks"""
    try:
        # Scan all task keys and get the 50 most recent ones
        tasks = []
        cursor = 0
        scan_count = 0
        
        while True:
            cursor, keys = redis_client.scan(cursor, match='task:*', count=100)
            
            for key in keys:
                task_data = redis_client.get(key)
                if task_data:
                    task = json.loads(task_data)
                    tasks.append(task)
            
            if cursor == 0:
                break
        
        # Sort by created_at and get last 50
        tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        recent_tasks = tasks[:50]
        
        return jsonify({
            'tasks': recent_tasks,
            'total': len(tasks),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dlq')
def get_dlq_tasks():
    """Get tasks in the dead letter queue"""
    try:
        dlq_size = redis_client.llen('dlq:failed_tasks')
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def get_metrics():
    """Get Prometheus metrics"""
    try:
        # This would call the gateway metrics endpoint
        # For now, return a simple response
        return jsonify({
            'message': 'Metrics available at /metrics endpoint'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    print("[Dashboard] Starting task queue dashboard...")
    app.run(host='0.0.0.0', port=5001, debug=False)
