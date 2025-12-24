# src/worker/worker.py
import redis
import json
import uuid
import time
import os
import signal
import sys
from datetime import datetime
import threading
import random

class WorkerNode:
    # Retry configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    INITIAL_RETRY_DELAY = int(os.getenv('INITIAL_RETRY_DELAY', 5))  # seconds
    RETRY_BACKOFF_MULTIPLIER = float(os.getenv('RETRY_BACKOFF_MULTIPLIER', 2.0))
    MAX_RETRY_DELAY = int(os.getenv('MAX_RETRY_DELAY', 3600))  # 1 hour
    
    def __init__(self):
        self.worker_id = f"worker-{str(uuid.uuid4())[:8]}"
        self.is_running = False
        self.current_task = None
        
        # Redis configuration
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        # Redis clients
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry_on_timeout=True
        )
        
        # Separate client for pub/sub
        self.pubsub = self.redis_client.pubsub()
        
    def start(self):
        """Start the worker node"""
        try:
            self.is_running = True
            self.register()
            self.setup_subscriptions()
            
            # Start heartbeat in background thread
            heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
            heartbeat_thread.start()
            
            # Start retry processor thread
            retry_thread = threading.Thread(target=self.retry_processor_loop, daemon=True)
            retry_thread.start()
            
            print(f"[{self.worker_id}] Worker started and ready for tasks")
            
            # Start processing tasks
            self.process_tasks_loop()
            
        except Exception as e:
            print(f"[{self.worker_id}] Failed to start: {e}")
            sys.exit(1)
    
    def register(self):
        """Register worker in the cluster"""
        worker_info = {
            'id': self.worker_id,
            'status': 'active',
            'started_at': datetime.utcnow().isoformat(),
            'tasks_processed': 0,
            'last_heartbeat': datetime.utcnow().isoformat()
        }
        
        self.redis_client.sadd('workers:active', self.worker_id)
        self.redis_client.set(f'worker:{self.worker_id}', json.dumps(worker_info))
        print(f"[{self.worker_id}] Registered in cluster")
    
    def setup_subscriptions(self):
        """Subscribe to task notifications"""
        self.pubsub.subscribe('tasks:new')
        
        # Start listening thread
        def listen():
            for message in self.pubsub.listen():
                if message['type'] == 'message' and not self.current_task:
                    print(f"[{self.worker_id}] Notified of new task")
        
        listener_thread = threading.Thread(target=listen, daemon=True)
        listener_thread.start()
    
    def heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.is_running:
            try:
                worker_data = self.redis_client.get(f'worker:{self.worker_id}')
                if worker_data:
                    worker = json.loads(worker_data)
                    worker['last_heartbeat'] = datetime.utcnow().isoformat()
                    worker['current_task'] = self.current_task
                    self.redis_client.set(f'worker:{self.worker_id}', json.dumps(worker))
            except Exception as e:
                print(f"[{self.worker_id}] Heartbeat failed: {e}")
            
            time.sleep(5)
    
    def process_tasks_loop(self):
        """Main task processing loop"""
        while self.is_running:
            try:
                self.process_next_task()
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[{self.worker_id}] Error in task loop: {e}")
                time.sleep(2)
    
    def process_next_task(self):
        """Process the next available task"""
        if self.current_task:
            return
        
        try:
            # Try high priority queue first
            task_id = self.redis_client.rpop('tasks:pending:high')
            priority = 'high'
            
            # If no high priority tasks, try normal queue
            if not task_id:
                task_id = self.redis_client.rpop('tasks:pending')
                priority = 'normal'
            
            if not task_id:
                return
            
            self.current_task = task_id
            task_data = self.redis_client.get(f'task:{task_id}')
            
            if not task_data:
                print(f"[{self.worker_id}] ❌ Task {task_id} not found in Redis")
                self.current_task = None
                return
            
            task = json.loads(task_data)
            print(f"[{self.worker_id}] 📋 ASSIGNED task {task_id} | Type: {task.get('type')} | Priority: {priority}")
            
            # Update task status
            task['status'] = 'processing'
            task['worker_id'] = self.worker_id
            task['started_at'] = datetime.utcnow().isoformat()
            self.redis_client.set(f'task:{task_id}', json.dumps(task))
            
            print(f"[{self.worker_id}] ⚙️  STARTED processing task {task_id}")
            
            # Execute the task
            result = self.execute_task(task)
            
            # Update task with result
            task['status'] = 'completed'
            task['completed_at'] = datetime.utcnow().isoformat()
            task['result'] = result
            task['retry_count'] = task.get('retry_count', 0)
            self.redis_client.set(f'task:{task_id}', json.dumps(task))
            
            # Increment completed counter
            self.redis_client.incr('tasks:completed')
            
            # Update worker stats
            worker_data = self.redis_client.get(f'worker:{self.worker_id}')
            if worker_data:
                worker = json.loads(worker_data)
                worker['tasks_processed'] = worker.get('tasks_processed', 0) + 1
                self.redis_client.set(f'worker:{self.worker_id}', json.dumps(worker))
            
            print(f"[{self.worker_id}] ✅ COMPLETED task {task_id}")
            self.current_task = None
            
        except Exception as e:
            print(f"[{self.worker_id}] ❌ ERROR processing task {self.current_task}: {e}")
            
            if self.current_task:
                try:
                    task_data = self.redis_client.get(f'task:{self.current_task}')
                    if task_data:
                        task = json.loads(task_data)
                        retry_count = task.get('retry_count', 0)
                        
                        if retry_count < self.MAX_RETRIES:
                            # Schedule retry with exponential backoff
                            retry_delay = min(
                                self.INITIAL_RETRY_DELAY * (self.RETRY_BACKOFF_MULTIPLIER ** retry_count),
                                self.MAX_RETRY_DELAY
                            )
                            retry_at = datetime.utcnow().timestamp() + retry_delay
                            
                            task['status'] = 'retrying'
                            task['retry_count'] = retry_count + 1
                            task['error'] = str(e)
                            task['last_error_at'] = datetime.utcnow().isoformat()
                            task['retry_at'] = retry_at
                            self.redis_client.set(f'task:{self.current_task}', json.dumps(task))
                            
                            # Add to retry queue with delay
                            self.redis_client.zadd('tasks:retry', {self.current_task: retry_at})
                            
                            print(f"[{self.worker_id}] 🔄 Task {self.current_task} scheduled for retry #{retry_count + 1} in {retry_delay:.1f}s")
                        else:
                            # Max retries exceeded - send to DLQ
                            task['status'] = 'failed'
                            task['error'] = str(e)
                            task['failed_at'] = datetime.utcnow().isoformat()
                            task['retry_count'] = retry_count
                            self.redis_client.set(f'task:{self.current_task}', json.dumps(task))
                            
                            # Add to dead letter queue
                            self.redis_client.lpush('dlq:failed_tasks', self.current_task)
                            
                            print(f"[{self.worker_id}] 💀 Task {self.current_task} moved to DLQ after {retry_count} retries")
                except Exception as ex:
                    print(f"[{self.worker_id}] ⚠️  Failed to update task status: {ex}")
                
                self.current_task = None
    
    def execute_task(self, task):
        """Execute a task based on its type"""
        # Simulate processing time
        processing_time = random.uniform(1, 4)
        task_id = task.get('id')
        print(f"[{self.worker_id}] ⏱️  Task {task_id} processing... (simulated delay: {processing_time:.2f}s)")
        time.sleep(processing_time)
        
        task_type = task.get('type')
        task_data = task.get('data')
        
        if task_type == 'process':
            return {
                'processed': task_data,
                'length': len(str(task_data)),
                'uppercase': str(task_data).upper(),
                'timestamp': datetime.utcnow().isoformat()
            }
        elif task_type == 'calculate':
            return {
                'input': task_data,
                'result': task_data * 2 if isinstance(task_data, (int, float)) else None,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'message': 'Task processed successfully',
                'data': task_data,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def retry_processor_loop(self):
        """Process tasks scheduled for retry"""
        while self.is_running:
            try:
                current_time = datetime.utcnow().timestamp()
                
                # Get tasks ready for retry (score <= current time)
                retry_tasks = self.redis_client.zrangebyscore('tasks:retry', 0, current_time)
                
                for task_id in retry_tasks:
                    try:
                        # Move back to pending queue
                        priority_key = self.redis_client.get(f'task:{task_id}:priority') or 'normal'
                        queue_key = 'tasks:pending:high' if priority_key == 'high' else 'tasks:pending'
                        self.redis_client.lpush(queue_key, task_id)
                        
                        # Remove from retry queue
                        self.redis_client.zrem('tasks:retry', task_id)
                        
                        task_data = self.redis_client.get(f'task:{task_id}')
                        if task_data:
                            task = json.loads(task_data)
                            retry_count = task.get('retry_count', 0)
                            print(f"[{self.worker_id}] 🔔 Requeued task {task_id} for retry #{retry_count}")
                    except Exception as e:
                        print(f"[{self.worker_id}] ⚠️  Failed to requeue task {task_id}: {e}")
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"[{self.worker_id}] ⚠️  Error in retry processor: {e}")
                time.sleep(10)
    
    def shutdown(self):
        """Graceful shutdown"""
        print(f"[{self.worker_id}] Shutting down...")
        self.is_running = False
        
        try:
            # Deregister from cluster
            self.redis_client.srem('workers:active', self.worker_id)
            self.redis_client.delete(f'worker:{self.worker_id}')
            
            # Close connections
            self.pubsub.close()
            self.redis_client.close()
        except Exception as e:
            print(f"[{self.worker_id}] Error during shutdown: {e}")
        
        print(f"[{self.worker_id}] Shutdown complete")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\nReceived shutdown signal...")
    if 'worker' in globals():
        worker.shutdown()
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start worker
    worker = WorkerNode()
    worker.start()