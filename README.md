# Distributed Task Queue System (Python)

A hands-on learning project for understanding distributed systems concepts through building a real-time task queue with Python.

## 🎯 What You'll Learn

This project demonstrates key distributed systems concepts:

- **Service Discovery**: Workers automatically register and deregister
- **Load Balancing**: Tasks distributed across multiple worker nodes  
- **Fault Tolerance**: System continues working when nodes fail
- **State Management**: Shared state coordination using Redis
- **Health Monitoring**: Real-time system health tracking
- **Message Passing**: Pub/Sub communication between components
- **Priority Queues**: High-priority task handling
- **Heartbeat Mechanism**: Detecting failed nodes

## 📋 Prerequisites

- Python 3.8 or higher
- Redis 5.0 or higher
- pip (Python package manager)
- Git
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### 1. Clone or Create the Project

```bash
# Create project directory
mkdir distributed-task-queue-python
cd distributed-task-queue-python

# Initialize git
git init

# Create directory structure
mkdir -p src/gateway src/worker src/shared tests
touch src/shared/__init__.py
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install flask redis requests python-dotenv gunicorn
```

### 3. Create requirements.txt

```bash
cat > requirements.txt << EOF
flask==3.0.0
redis==5.0.1
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
EOF
```

### 4. Start Redis

**Option A: Using Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

**Option B: Local Installation**
```bash
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

### 5. Run the System

Open 5 separate terminal windows:

**Terminal 1 - Gateway**
```bash
source venv/bin/activate
python src/gateway/server.py
```

**Terminals 2-4 - Workers**
```bash
source venv/bin/activate
python src/worker/worker.py
# Run this in 3 different terminals
```

**Terminal 5 - Test Commands**
```bash
# Submit a task
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type": "process", "data": "Hello Distributed Systems!"}'

# Check system health
curl http://localhost:5000/health

# View all tasks
curl http://localhost:5000/tasks

# View active workers
curl http://localhost:5000/workers

# Get specific task status
curl http://localhost:5000/tasks/{TASK_ID}
```

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker1=5

# Stop all services
docker-compose down
```

## 🧪 Learning Experiments

### Experiment 1: Worker Failure & Recovery

**Goal**: Understand fault tolerance

```bash
# 1. Start system with 3 workers
python src/gateway/server.py &
python src/worker/worker.py &
python src/worker/worker.py &
python src/worker/worker.py &

# 2. Submit 50 tasks
python tests/stress_test.py

# 3. Kill one worker (Ctrl+C in that terminal)

# 4. Observe in logs:
#    - Task redistribution
#    - Worker count decrease in health endpoint
#    - System continues processing

# 5. Check health
curl http://localhost:5000/health
```

**Expected Behavior**:
- Remaining workers pick up pending tasks
- No tasks are lost
- Processing continues seamlessly

### Experiment 2: Dynamic Scaling

**Goal**: See horizontal scaling in action

```bash
# 1. Start with 2 workers
python src/worker/worker.py &
python src/worker/worker.py &

# 2. Check initial throughput
python tests/stress_test.py

# 3. While tasks are running, add 3 more workers
python src/worker/worker.py &
python src/worker/worker.py &
python src/worker/worker.py &

# 4. Watch throughput increase in real-time
```

**What to Observe**:
- New workers automatically join cluster
- Tasks per second increases
- Load distributes evenly

### Experiment 3: Priority Queue Testing

**Goal**: Understand task prioritization

```bash
# Submit 10 normal priority tasks
for i in {1..10}; do
  curl -X POST http://localhost:5000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"process\", \"data\": \"Normal $i\", \"priority\": \"normal\"}"
done

# Submit 5 high priority tasks
for i in {1..5}; do
  curl -X POST http://localhost:5000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"process\", \"data\": \"Urgent $i\", \"priority\": \"high\"}"
done

# Watch logs - high priority tasks processed first
```

### Experiment 4: Monitoring Redis State

**Goal**: Understand distributed state management

```bash
# Connect to Redis
redis-cli

# Watch all commands in real-time
MONITOR

# In another terminal, submit tasks and watch Redis operations

# Useful Redis commands:
KEYS worker:*              # List all workers
KEYS task:*                # List all tasks
SMEMBERS workers:active    # Active workers
LLEN tasks:pending         # Pending task count
GET task:{TASK_ID}         # Task details
```

### Experiment 5: Stress Testing

**Goal**: Test system under load

```bash
# Run stress test with 100 tasks
python tests/stress_test.py

# Modify stress_test.py to increase load:
# TOTAL_TASKS = 500  # or 1000

# Monitor:
# - Task completion rate
# - Worker utilization
# - System stability
```

## 🏗️ Architecture Deep Dive

```
┌─────────────────────────────────────────┐
│            Client / User                │
└──────────────┬──────────────────────────┘
               │ HTTP POST/GET
               ▼
┌─────────────────────────────────────────┐
│         API Gateway (Flask)             │
│  • Task submission endpoint             │
│  • Task status queries                  │
│  • Worker health monitoring             │
│  • Redis state coordination             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           Redis (State Store)           │
│                                         │
│  Lists:   • tasks:pending (FIFO)       │
│           • tasks:pending:high          │
│                                         │
│  Sets:    • workers:active              │
│                                         │
│  Strings: • task:{id} (metadata)       │
│           • worker:{id} (info)          │
│           • tasks:completed (counter)   │
│                                         │
│  Pub/Sub: • tasks:new (notifications)  │
└──────────────┬──────────────────────────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
   ┌───────┐┌───────┐┌───────┐
   │Worker││Worker││Worker│
   │  #1  ││  #2  ││  #3  │
   └───────┘└───────┘└───────┘
```

### Data Flow

1. **Task Submission**:
   - Client → Gateway (HTTP POST)
   - Gateway → Redis (Store metadata, Add to queue)
   - Gateway → Redis Pub/Sub (Notify workers)

2. **Task Processing**:
   - Worker → Redis (RPOP from queue)
   - Worker → Redis (Update task status)
   - Worker → Execute task
   - Worker → Redis (Store result)

3. **Health Monitoring**:
   - Workers → Redis (Heartbeat every 5s)
   - Gateway → Redis (Query worker registry)
   - Client → Gateway (GET /health)

## 📊 API Reference

### POST /tasks
Submit a new task

**Request**:
```json
{
  "type": "process",
  "data": "Some data to process",
  "priority": "normal"
}
```

**Response**:
```json
{
  "success": true,
  "task_id": "uuid-here",
  "message": "Task submitted successfully"
}
```

### GET /health
Get system health

**Response**:
```json
{
  "status": "healthy",
  "gateway": "gateway-abc123",
  "workers": 3,
  "pending_tasks": 15,
  "completed_tasks": 42,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### GET /tasks
List all tasks (with optional filtering)

**Query Parameters**:
- `status`: Filter by status (pending, processing, completed, failed)
- `limit`: Maximum tasks to return (default: 50)

### GET /tasks/{task_id}
Get specific task status

### GET /workers
List all active workers

## 🔧 Advanced Exercises

### Exercise 1: Implement Task Retry Logic

Add automatic retry for failed tasks:

```python
# In worker.py, modify process_next_task()
def process_next_task(self):
    # ... existing code ...
    
    try:
        result = self.execute_task(task)
        # ... success handling ...
    except Exception as e:
        retry_count = task.get('retry_count', 0)
        if retry_count < 3:
            # Re-queue with exponential backoff
            task['retry_count'] = retry_count + 1
            time.sleep(2 ** retry_count)  # 2, 4, 8 seconds
            self.redis_client.lpush('tasks:pending', task_id)
        else:
            # Move to dead letter queue
            self.redis_client.lpush('tasks:dead_letter', task_id)
```

### Exercise 2: Add Performance Metrics

Track detailed metrics:

```python
# Create src/shared/metrics.py
class Metrics:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def record_task_time(self, task_id, duration):
        self.redis.zadd('metrics:task_times', {task_id: duration})
    
    def get_avg_task_time(self):
        times = self.redis.zrange('metrics:task_times', 0, -1, withscores=True)
        return sum(score for _, score in times) / len(times) if times else 0
```

### Exercise 3: Build a Web Dashboard

Create a real-time monitoring dashboard:

```python
# src/gateway/dashboard.py
from flask import render_template
import plotly.graph_objs as go

@app.route('/dashboard')
def dashboard():
    # Fetch metrics from Redis
    # Create visualizations with Plotly
    # Return HTML template
    pass
```

### Exercise 4: Implement Task Dependencies

Allow tasks to depend on other tasks:

```python
# Add to task schema
{
    "id": "task-2",
    "depends_on": ["task-1"],  # Wait for task-1 to complete
    # ... rest of task
}
```

### Exercise 5: Add Distributed Tracing

Integrate OpenTelemetry for tracing:

```bash
pip install opentelemetry-api opentelemetry-sdk
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Add spans to track task flow
with tracer.start_as_current_span("process_task"):
    result = self.execute_task(task)
```

## 🐛 Troubleshooting

### Workers Not Processing Tasks

```bash
# Check if workers are registered
curl http://localhost:5000/workers

# Check Redis connection
redis-cli ping

# View worker logs for errors
# Check if tasks are in queue
redis-cli LLEN tasks:pending
```

### Tasks Stuck in Pending State

```bash
# Check worker count
curl http://localhost:5000/health

# Manually inspect task
redis-cli GET task:{TASK_ID}

# Check for errors in worker logs
```

### Gateway Won't Start

```bash
# Port already in use
# Change port: export PORT=5001

# Redis connection failed
# Verify Redis: redis-cli ping
# Check REDIS_HOST and REDIS_PORT environment variables
```

### High Memory Usage

```bash
# Check Redis memory
redis-cli INFO memory

# Clear completed tasks (manual cleanup)
redis-cli KEYS "task:*" | xargs redis-cli DEL

# Implement automatic cleanup:
# Delete tasks older than 1 hour
```

## 📝 Best Practices

1. **Always use virtual environments**
2. **Set appropriate timeouts** for Redis connections
3. **Implement graceful shutdown** (already included)
4. **Log important events** for debugging
5. **Monitor Redis memory** usage
6. **Use connection pooling** for high throughput
7. **Implement rate limiting** for API endpoints
8. **Add authentication** for production use

## 🎓 Learning Path

**Week 1**: Set up and run the basic system
- Understand the architecture
- Run all test commands
- Monitor Redis state

**Week 2**: Experiments and failure scenarios
- Complete all 5 experiments
- Observe system behavior
- Document your findings

**Week 3**: Code deep-dive
- Read and understand each component
- Modify worker logic
- Add custom task types

**Week 4**: Advanced features
- Implement retry logic
- Add metrics collection
- Build monitoring dashboard

**Week 5**: Production readiness
- Add authentication
- Implement rate limiting
- Set up logging and monitoring
- Deploy with Docker

## 📚 Additional Resources

- **Redis Documentation**: https://redis.io/docs/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Python Threading**: https://docs.python.org/3/library/threading.html
- **Distributed Systems Theory**: 
  - "Designing Data-Intensive Applications" by Martin Kleppmann
  - "Building Microservices" by Sam Newman

## 🤝 Contributing

This is a learning project! Feel free to:
- Add new features
- Improve documentation
- Share your experiments
- Submit issues or PRs

## 📄 License

MIT License - use freely for learning!

---

**Happy Learning! 🚀**

*The best way to learn distributed systems is by building them. Break things, fix them, and learn from the experience!*