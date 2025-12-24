# Command Reference & Cheat Sheet

## 🚀 Quick Commands

### Start Services
```bash
# Start all services
docker-compose up -d --build

# Start and see logs
docker-compose up --build

# Start specific service
docker-compose up -d gateway
```

### Stop Services
```bash
# Stop all services
docker-compose stop

# Stop and remove
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

### Check Status
```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs task-queue-gateway
docker logs task-queue-worker-1
docker logs task-queue-dashboard

# Follow logs in real-time
docker logs -f task-queue-gateway

# View logs since specific time
docker logs --since 5m task-queue-gateway
```

---

## 🔌 API Commands

### Submit Tasks
```bash
# Simple task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"process","data":"hello"}'

# With priority
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"calculate","data":42,"priority":"high"}'

# Process type
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"process","data":"some text"}'

# Calculate type
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"calculate","data":100}'
```

### Get Task Status
```bash
# Get specific task
curl http://localhost:8000/tasks/{TASK_ID}

# Get all tasks
curl http://localhost:8000/tasks

# Get with pretty print
curl http://localhost:8000/tasks/{TASK_ID} | python -m json.tool
```

### System Status
```bash
# Health check
curl http://localhost:8000/health

# List workers
curl http://localhost:8000/workers

# Health with pretty print
curl http://localhost:8000/health | python -m json.tool
```

### Metrics
```bash
# Get all metrics
curl http://localhost:8000/metrics

# Get specific metric
curl http://localhost:8000/metrics | grep task_submissions_total

# Save to file
curl http://localhost:8000/metrics > metrics.txt
```

### Dead Letter Queue
```bash
# List DLQ tasks
curl http://localhost:8000/dlq/failed-tasks

# List DLQ with pretty print
curl http://localhost:8000/dlq/failed-tasks | python -m json.tool

# Retry a task
curl -X POST http://localhost:8000/dlq/failed-tasks/{TASK_ID}/retry

# Remove from DLQ
curl -X DELETE http://localhost:8000/dlq/failed-tasks/{TASK_ID}
```

---

## 📊 Dashboard Commands

### Access Services
```bash
# Dashboard UI
open http://localhost:5001

# API endpoints
curl http://localhost:5001/api/stats
curl http://localhost:5001/api/tasks/recent
curl http://localhost:5001/api/dlq

# Pretty print
curl http://localhost:5001/api/stats | python -m json.tool
```

---

## 🔍 Monitoring Commands

### Prometheus
```bash
# Access Prometheus
open http://localhost:9090

# Query specific metric
curl 'http://localhost:9090/api/v1/query?query=task_submissions_total'

# Get targets status
curl http://localhost:9090/api/v1/targets
```

### Jaeger
```bash
# Access Jaeger UI
open http://localhost:16686

# Get available services
curl http://localhost:16686/api/services
```

---

## 🐳 Docker Commands

### Container Management
```bash
# List containers
docker ps -a

# View container details
docker inspect task-queue-gateway

# Stats (CPU, memory, network)
docker stats

# Continuous stats
watch docker stats

# View container logs
docker logs -f task-queue-worker-1

# View last 100 lines
docker logs --tail 100 task-queue-gateway

# View logs with timestamps
docker logs --timestamps task-queue-gateway

# View logs since 30 minutes ago
docker logs --since 30m task-queue-gateway
```

### Debugging
```bash
# Execute command in container
docker exec task-queue-gateway python --version

# Open shell in container
docker exec -it task-queue-gateway /bin/sh

# View network
docker network ls

# Inspect network
docker network inspect distributed-task-queue-python_default
```

---

## 🔴 Redis Commands

### Redis CLI
```bash
# Connect to Redis
redis-cli -h localhost -p 6379

# Check connection
redis-cli PING

# Get info
redis-cli INFO

# Get all keys
redis-cli KEYS '*'

# Get specific key
redis-cli GET task:{TASK_ID}

# Get all task keys
redis-cli KEYS 'task:*'

# Get queue length
redis-cli LLEN tasks:pending
redis-cli LLEN tasks:pending:high
redis-cli LLEN dlq:failed_tasks

# Get retry queue
redis-cli ZRANGE tasks:retry 0 -1 WITHSCORES

# Clear a queue
redis-cli DEL tasks:pending
redis-cli DEL dlq:failed_tasks

# Monitor Redis commands
redis-cli MONITOR

# Get all metrics
redis-cli INFO stats
```

### Bulk Operations
```bash
# Count all tasks
redis-cli KEYS 'task:*' | wc -l

# Get all task IDs
redis-cli KEYS 'task:*' | head -10

# Delete all retry tasks
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', 'tasks:retry')))" 0

# Clear completed counter
redis-cli SET tasks:completed 0
```

---

## 📝 Testing Commands

### Run Tests
```bash
# Run stress test
python tests/stress_test.py

# Run test client (interactive)
python tests/test_client.py

# Submit 10 tasks
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"type":"process","data":"test-'$i'"}'
done

# Submit with different priorities
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"process","data":"test","priority":"high"}'
```

### Performance Testing
```bash
# Generate load (100 tasks)
for i in {1..100}; do
  curl -s -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"type":"calculate","data":42}' &
done
wait

# Monitor while testing
watch 'curl -s http://localhost:8000/health | python -m json.tool'

# Check throughput
time python tests/stress_test.py
```

---

## 🔗 URL Quick Links

### Local Access
```
Gateway API:     http://localhost:8000
Dashboard:       http://localhost:5001
Prometheus:      http://localhost:9090
Jaeger:          http://localhost:16686
Redis:           localhost:6379
```

### API Endpoints
```
Health:          http://localhost:8000/health
Metrics:         http://localhost:8000/metrics
Tasks:           http://localhost:8000/tasks
Workers:         http://localhost:8000/workers
DLQ:             http://localhost:8000/dlq/failed-tasks
```

### Dashboard Endpoints
```
Stats:           http://localhost:5001/api/stats
Recent Tasks:    http://localhost:5001/api/tasks/recent
DLQ:             http://localhost:5001/api/dlq
```

### Monitoring
```
Prometheus:      http://localhost:9090
Jaeger:          http://localhost:16686
```

---

## 📊 Common Queries

### Task Statistics
```bash
# Count completed tasks
curl http://localhost:8000/health | jq '.completed_tasks'

# Count pending tasks
curl http://localhost:8000/health | jq '.pending_tasks'

# Count workers
curl http://localhost:8000/health | jq '.workers'

# Get dashboard stats
curl http://localhost:5001/api/stats | jq '.tasks'
```

### Log Filtering
```bash
# Show only task assignments
docker logs task-queue-worker-1 | grep "ASSIGNED"

# Show retries
docker logs task-queue-worker-1 | grep "🔄"

# Show completions
docker logs task-queue-worker-1 | grep "COMPLETED"

# Show errors
docker logs task-queue-worker-1 | grep "ERROR"

# Show submissions
docker logs task-queue-gateway | grep "SUBMITTED"

# Show last 50 lines
docker logs --tail 50 task-queue-gateway
```

---

## 🎯 Troubleshooting Commands

### Check Connectivity
```bash
# Test gateway
curl http://localhost:8000/health

# Test dashboard
curl http://localhost:5001

# Test Redis
redis-cli PING

# Test Prometheus
curl http://localhost:9090/-/healthy

# Test Jaeger
curl http://localhost:16686/api/services
```

### View Service Status
```bash
# All services
docker-compose ps

# Specific service
docker inspect task-queue-gateway | grep -E "State|Status"

# Memory usage
docker stats --no-stream

# Network connections
docker inspect task-queue-gateway | grep -A 10 'NetworkSettings'
```

### Debug Imports
```bash
# Check if metrics module exists
docker exec task-queue-gateway python -c "from src.shared.metrics import *"

# Check Python path
docker exec task-queue-gateway python -c "import sys; print(sys.path)"

# List files in container
docker exec task-queue-gateway ls -la src/shared/
```

---

## 🔧 Configuration Commands

### Set Environment Variables
```bash
# In docker-compose.yml
environment:
  - MAX_RETRIES=3
  - INITIAL_RETRY_DELAY=5
  - RETRY_BACKOFF_MULTIPLIER=2.0

# Rebuild after changes
docker-compose up -d --build
```

### Scale Services
```bash
# Scale workers in Kubernetes
kubectl scale deployment worker -n task-queue --replicas=5

# Docker Compose (create multiple instances)
docker-compose up -d --scale worker=5
```

---

## 📈 Performance Monitoring

### Real-time Monitoring
```bash
# Watch stats update
watch 'curl -s http://localhost:8000/health | python -m json.tool'

# Watch specific metric
watch 'curl -s http://localhost:8000/metrics | grep task_completions_total'

# Watch container stats
watch docker stats --no-stream

# Watch Redis memory
watch 'redis-cli INFO memory'
```

### Collect Metrics
```bash
# Export metrics
curl http://localhost:8000/metrics > metrics_$(date +%s).txt

# Export to Prometheus format
curl http://localhost:9090/api/v1/query?query=task_submissions_total > metrics.json

# Check processing rate
curl http://localhost:9090/api/v1/query?query='rate(task_completions_total[1m])'
```

---

## 🐛 Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
lsof -i :5001
lsof -i :9090

# Kill process
kill -9 <PID>
```

### Container Won't Start
```bash
# Check logs
docker logs task-queue-gateway

# Check for port conflicts
netstat -an | grep LISTEN

# Restart service
docker-compose restart gateway
```

### Redis Connection Issues
```bash
# Test Redis
redis-cli PING

# Check Redis is running
docker exec task-queue-redis redis-cli PING

# Check network
docker network inspect distributed-task-queue-python_default
```

### Memory Issues
```bash
# Check container memory
docker stats

# Check Redis memory
redis-cli INFO memory | grep used_memory_human

# Clear old tasks (use carefully)
redis-cli FLUSHDB  # WARNING: Clears entire database
```

---

## 💾 Backup & Recovery

### Backup Redis Data
```bash
# Backup Redis data
docker exec task-queue-redis redis-cli BGSAVE

# Copy backup file
docker cp task-queue-redis:/data/dump.rdb ./backup.rdb

# Restore from backup
docker cp ./backup.rdb task-queue-redis:/data/
```

### Export Task Data
```bash
# Export all tasks as JSON
redis-cli KEYS 'task:*' | while read key; do
  redis-cli GET $key
done > tasks_backup.json

# Count tasks
redis-cli KEYS 'task:*' | wc -l
```

---

## 📚 Documentation Files

```
FEATURES_SUMMARY.md     # Complete feature overview
ADVANCED_FEATURES.md    # Detailed feature documentation
QUICK_START_FEATURES.md # Quick start with examples
COMMAND_REFERENCE.md    # This file - command cheat sheet
```

---

**Pro Tip:** Save this file and use `Ctrl+F` to search for the command you need! 🚀

