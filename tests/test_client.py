# tests/test_client.py
"""
Interactive test client for the distributed task queue system.
Run this to easily test the system without using curl commands.
"""

import requests
import json
import time
import sys

GATEWAY_URL = 'http://localhost:8000'

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def check_health():
    """Check system health"""
    print_header("System Health Check")
    try:
        response = requests.get(f'{GATEWAY_URL}/health', timeout=5)
        health = response.json()
        
        print(f"Status:           {health['status']}")
        print(f"Gateway ID:       {health['gateway']}")
        print(f"Active Workers:   {health['workers']}")
        print(f"Pending Tasks:    {health['pending_tasks']}")
        print(f"Completed Tasks:  {health['completed_tasks']}")
        print(f"Timestamp:        {health['timestamp']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def submit_task(task_type='process', data='Test data', priority='normal'):
    """Submit a task"""
    print_header("Submitting Task")
    
    payload = {
        'type': task_type,
        'data': data,
        'priority': priority
    }
    
    print(f"Task Type: {task_type}")
    print(f"Data:      {data}")
    print(f"Priority:  {priority}")
    
    try:
        response = requests.post(
            f'{GATEWAY_URL}/tasks',
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✅ Task submitted successfully!")
            print(f"Task ID: {result['task_id']}")
            return result['task_id']
        else:
            print(f"\n❌ Failed: {response.text}")
            return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def get_task(task_id):
    """Get task status"""
    print_header(f"Task Status: {task_id}")
    
    try:
        response = requests.get(f'{GATEWAY_URL}/tasks/{task_id}', timeout=5)
        
        if response.status_code == 200:
            task = response.json()
            print(f"ID:         {task['id']}")
            print(f"Type:       {task['type']}")
            print(f"Status:     {task['status']}")
            print(f"Priority:   {task['priority']}")
            print(f"Created:    {task['created_at']}")
            
            if 'worker_id' in task:
                print(f"Worker:     {task['worker_id']}")
            if 'result' in task:
                print(f"\nResult:")
                print_json(task['result'])
        else:
            print(f"❌ Task not found")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_tasks(status=None):
    """List all tasks"""
    print_header("All Tasks")
    
    try:
        params = {}
        if status:
            params['status'] = status
        
        response = requests.get(f'{GATEWAY_URL}/tasks', params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tasks = data['tasks']
            
            print(f"Total tasks: {data['count']}")
            
            if tasks:
                print("\nTasks:")
                for task in tasks[:10]:  # Show first 10
                    print(f"  • {task['id'][:8]}... - {task['status']} - {task['type']}")
            else:
                print("No tasks found")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_workers():
    """List all workers"""
    print_header("Active Workers")
    
    try:
        response = requests.get(f'{GATEWAY_URL}/workers', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            workers = data['workers']
            
            print(f"Total workers: {data['count']}")
            
            if workers:
                print("\nWorkers:")
                for worker in workers:
                    print(f"\n  ID:              {worker['id']}")
                    print(f"  Status:          {worker['status']}")
                    print(f"  Tasks Processed: {worker['tasks_processed']}")
                    print(f"  Last Heartbeat:  {worker['last_heartbeat']}")
            else:
                print("No active workers")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def monitor_task(task_id, timeout=30):
    """Monitor a task until completion"""
    print_header(f"Monitoring Task: {task_id}")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'{GATEWAY_URL}/tasks/{task_id}', timeout=5)
            
            if response.status_code == 200:
                task = response.json()
                status = task['status']
                
                if status != last_status:
                    print(f"[{time.strftime('%H:%M:%S')}] Status: {status}")
                    last_status = status
                
                if status in ['completed', 'failed']:
                    print(f"\n✅ Task finished with status: {status}")
                    if 'result' in task:
                        print("\nResult:")
                        print_json(task['result'])
                    return
            
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)
    
    print(f"\n⏱️  Timeout reached after {timeout}s")

def interactive_menu():
    """Show interactive menu"""
    while True:
        print("\n" + "=" * 60)
        print("  Distributed Task Queue - Test Client")
        print("=" * 60)
        print("\n1. Check system health")
        print("2. Submit a task")
        print("3. Get task status")
        print("4. List all tasks")
        print("5. List active workers")
        print("6. Submit and monitor task")
        print("7. Submit 10 test tasks")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '0':
            print("\nGoodbye! 👋")
            break
        elif choice == '1':
            check_health()
        elif choice == '2':
            task_type = input("Task type (process/calculate): ").strip() or 'process'
            data = input("Data: ").strip() or 'Test data'
            priority = input("Priority (normal/high): ").strip() or 'normal'
            submit_task(task_type, data, priority)
        elif choice == '3':
            task_id = input("Task ID: ").strip()
            if task_id:
                get_task(task_id)
        elif choice == '4':
            status = input("Filter by status (or press Enter for all): ").strip() or None
            list_tasks(status)
        elif choice == '5':
            list_workers()
        elif choice == '6':
            task_type = input("Task type (process/calculate): ").strip() or 'process'
            data = input("Data: ").strip() or 'Test data'
            task_id = submit_task(task_type, data)
            if task_id:
                monitor_task(task_id)
        elif choice == '7':
            print("\nSubmitting 10 test tasks...")
            for i in range(10):
                task_id = submit_task('process', f'Test task {i+1}')
                if task_id:
                    print(f"  ✓ Task {i+1}/10 submitted")
                time.sleep(0.1)
            print("\n✅ All tasks submitted!")
        else:
            print("Invalid choice")

if __name__ == '__main__':
    print("\n🚀 Distributed Task Queue - Test Client")
    print("   Make sure the gateway is running on port 5000\n")
    
    # Check if gateway is available
    if not check_health():
        print("\n⚠️  Warning: Gateway is not responding")
        print("   Start the gateway first: python src/gateway/server.py")
        
        choice = input("\nContinue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            sys.exit(1)
    
    # Run interactive menu
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye! 👋")