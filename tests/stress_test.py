# tests/stress_test.py
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import string

GATEWAY_URL = 'http://localhost:8000'
TOTAL_TASKS = 1000

def generate_random_string(length=10):
    """Generate random string for task data"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def submit_task(task_number):
    """Submit a single task"""
    try:
        task_type = random.choice(['process', 'calculate'])
        
        if task_type == 'calculate':
            data = random.randint(1, 1000)
        else:
            data = f"Task {task_number} - {generate_random_string()}"
        
        payload = {
            'type': task_type,
            'data': data,
            'priority': 'high' if task_number % 10 == 0 else 'normal'
        }
        
        response = requests.post(
            f'{GATEWAY_URL}/tasks',
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            return {'success': True, 'task_number': task_number, 'data': response.json()}
        else:
            return {'success': False, 'task_number': task_number, 'error': response.text}
            
    except Exception as e:
        return {'success': False, 'task_number': task_number, 'error': str(e)}

def check_health():
    """Check system health"""
    try:
        response = requests.get(f'{GATEWAY_URL}/health', timeout=5)
        return response.json()
    except Exception as e:
        print(f"Error checking health: {e}")
        return None

def run_stress_test():
    """Run the stress test"""
    print(f"\n🚀 Starting stress test with {TOTAL_TASKS} tasks...\n")
    
    start_time = time.time()
    results = {'success': 0, 'failed': 0}
    
    # Submit all tasks concurrently
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(submit_task, i) for i in range(1, TOTAL_TASKS + 1)]
        
        for future in as_completed(futures):
            result = future.result()
            if result['success']:
                results['success'] += 1
                if result['task_number'] % 10 == 0:
                    print(f"✓ Submitted {result['task_number']}/{TOTAL_TASKS} tasks")
            else:
                results['failed'] += 1
                print(f"✗ Task {result['task_number']} failed: {result['error']}")
    
    submit_time = time.time() - start_time
    print(f"\n✅ Submission complete in {submit_time:.2f}s")
    print(f"   Success: {results['success']}, Failed: {results['failed']}")
    
    # Monitor completion
    print('\n⏳ Monitoring task completion...\n')
    
    last_completed = 0
    while True:
        time.sleep(1)
        
        health = check_health()
        if not health:
            continue
        
        completed = health.get('completed_tasks', 0)
        pending = health.get('pending_tasks', 0)
        workers = health.get('workers', 0)
        
        if completed != last_completed:
            print(f"   Completed: {completed}/{TOTAL_TASKS} | "
                  f"Pending: {pending} | Workers: {workers}")
            last_completed = completed
        
        if completed >= TOTAL_TASKS:
            break
    
    total_time = time.time() - start_time
    
    # Print final results
    print('\n' + '=' * 50)
    print('📊 STRESS TEST RESULTS')
    print('=' * 50)
    print(f"Total Tasks:       {TOTAL_TASKS}")
    print(f"Total Time:        {total_time:.2f}s")
    print(f"Throughput:        {TOTAL_TASKS / total_time:.2f} tasks/sec")
    print(f"Avg Task Time:     {(total_time / TOTAL_TASKS) * 1000:.2f}ms")
    print(f"Active Workers:    {workers}")
    print('=' * 50 + '\n')

if __name__ == '__main__':
    # Check if gateway is available
    print("Checking gateway availability...")
    health = check_health()
    
    if health:
        print(f"✓ Gateway is healthy")
        print(f"  Workers: {health.get('workers', 0)}")
        print(f"  Pending: {health.get('pending_tasks', 0)}")
        run_stress_test()
    else:
        print("❌ Gateway not available. Make sure it's running on port 5000")
        exit(1)