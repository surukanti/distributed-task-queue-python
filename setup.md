# Distributed Task Queue System (Python)

A real-time distributed system for learning core concepts through hands-on implementation.

## System Architecture

```
Client → API Gateway (Flask) → Worker Nodes (3+)
                            ↓
                    Redis (State Store)
                            ↓
                    Message Queue (Redis)
```

## What You'll Learn

1. **Service Discovery**: How nodes find and communicate with each other
2. **Load Balancing**: Distributing work across multiple workers
3. **Fault Tolerance**: Handling node failures gracefully
4. **Consensus**: Coordinating state across nodes
5. **Health Checks**: Monitoring system health
6. **Replication**: Ensuring data durability

## Prerequisites

- Python 3.8+
- Redis
- pip (Python package manager)
- Git

## Setup Instructions

### 1. Create GitHub Repository

```bash
# Create a new directory
mkdir distributed-task-queue-python
cd distributed-task-queue-python

# Initialize git
git init

# Create initial structure
mkdir -p src/{gateway,worker,shared} tests docs

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Create requirements.txt first (see artifact)
pip install -r requirements.txt
```

### 3. Project Structure

```
distributed-task-queue-python/
├── src/
│   ├── gateway/
│   │   └── server.py          # API Gateway (Flask)
│   ├── worker/
│   │   └── worker.py          # Worker Node
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration
│   │   └── utils.py           # Utilities
├── tests/
│   ├── stress_test.py
│   └── test_integration.py
├── requirements.txt
├── docker-compose.yml
├── README.md
└── .gitignore
```

### 4. Setup Redis

Install Redis or use Docker:

```bash
# Using Docker (Recommended)
docker run -d -p 6379:6379 --name redis redis:alpine

# Or install locally
# macOS: brew install redis && redis-server
# Ubuntu: sudo apt install redis-server && sudo systemctl start redis
```

### 5. Push to GitHub

```bash
# Create .gitignore
echo "venv/
__pycache__/
*.pyc
.env
.DS_Store" > .gitignore

# Stage all files
git add .

# Initial commit
git commit -m "Initial commit: Distributed Task Queue System (Python)"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/distributed-task-queue-python.git
git branch -M main
git push -u origin main
```

## Running the System

### Method 1: Manual (Multiple Terminals)

**Terminal 1 - Start Redis**
```bash
redis-server
```

**Terminal 2 - Start Gateway**
```bash
source venv/bin/activate
python src/gateway/server.py
```

**Terminal 3-5 - Start Worker Nodes**
```bash
source venv/bin/activate
python src/worker/worker.py
# Run in 3 separate terminals
```

### Method 2: Using Docker Compose

```bash
docker-compose up -d
```

## Testing the System

### Basic Commands

```bash
# Submit a task
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type": "process", "data": "Hello World"}'

# Check system health
curl http://localhost:5000/health

# View all tasks
curl http://localhost:5000/tasks

# Get specific task
curl http://localhost:5000/tasks/{TASK_ID}

# View active workers
curl http://localhost:5000/workers
```

### Run Stress Test

```bash
python tests/stress_test.py
```

## Learning Exercises

### 1. Kill a Worker Node
- Start 3 workers
- Submit 20 tasks
- Kill one worker (Ctrl+C)
- Observe task redistribution

### 2. Scale Up
- Start with 2 workers
- Submit 100 tasks
- Add 3 more workers while running
- Monitor throughput increase

### 3. Priority Queues
- Submit high and normal priority tasks
- Observe processing order

### 4. Monitor Redis
```bash
redis-cli
MONITOR  # Watch all commands
KEYS *   # See all keys
SMEMBERS workers:active
```

### 5. Network Partition
- Use Docker networks to simulate partition
- Observe system behavior

## Next Steps

After completing this project:
- Add a web dashboard (Flask + React)
- Implement distributed tracing
- Add task retry with exponential backoff
- Implement dead letter queue
- Add metrics and observability (Prometheus)
- Deploy to Kubernetes