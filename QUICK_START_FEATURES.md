# Quick Start Guide - Advanced Features

This guide helps you get started with all the new advanced features.

## 🚀 Immediate Getting Started (5 minutes)

### 1. Start the complete stack:
```bash
cd /Users/chinnareddy/go/src/github.com/chinnareddy578/distributed-task-queue-python
docker-compose up -d --build
```

### 2. Wait for services to be ready:
```bash
# Check status
docker-compose ps

# Expected output:
# - redis: healthy
# - gateway: running
# - worker1, worker2, worker3: running
# - dashboard: running
# - prometheus: running
# - jaeger: running
```

### 3. Access the services:
- **Dashboard**: http://localhost:5001
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686
- **API**: http://localhost:8000

## 📊 Feature Demonstrations

### A. Submit Tasks with Different Priorities
```bash
# High priority task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "process",
    "data": "important-task",
    "priority": "high"
  }'

# Normal priority task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "calculate",
    "data": 42,
    "priority": "normal"
  }'
```

### B. Watch Tasks Get Processed
```bash
# Terminal 1: Monitor gateway logs
docker logs -f task-queue-gateway

# Terminal 2: Monitor worker logs
docker logs -f task-queue-worker-1

# Terminal 3: Submit tasks
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"type":"process","data":"test-'$i'","priority":"normal"}' > /dev/null
  echo "Task $i submitted"
done
```

### C. View Metrics in Real-Time
```bash
# Raw Prometheus metrics
curl http://localhost:8000/metrics | grep task_submissions_total

# Or navigate to: http://localhost:9090
# Search for: task_submissions_total
```

### D. Monitor Dashboard
- Open http://localhost:5001 in browser
- Watch real-time statistics update
- See active workers and recent tasks
- Check Dead Letter Queue status

### E. Test Retry Mechanism
```bash
# Force a task to fail multiple times by submitting stress
python tests/stress_test.py

# Watch worker logs for retry messages:
# 🔄 Task scheduled for retry #1 in 5s
# 🔄 Task scheduled for retry #2 in 10s
# 💀 Task moved to DLQ after 3 retries
```

### F. Manage Dead Letter Queue
```bash
# View all failed tasks
curl http://localhost:8000/dlq/failed-tasks | python -m json.tool

# Retry a specific task (replace TASK_ID)
curl -X POST http://localhost:8000/dlq/failed-tasks/{TASK_ID}/retry

# Remove from DLQ
curl -X DELETE http://localhost:8000/dlq/failed-tasks/{TASK_ID}
```

### G. Trace Requests in Jaeger
1. Open http://localhost:16686
2. Select "gateway" service from dropdown
3. Click "Find Traces"
4. Click on a trace to see full request flow
5. View Redis operations, response times, errors

### H. View Prometheus Metrics
1. Open http://localhost:9090
2. Click "Graph" tab
3. Search for any of these:
   - `task_submissions_total`
   - `task_completions_total`
   - `task_duration_seconds`
   - `task_retries_total`
   - `tasks_in_dlq_total`
   - `active_workers_total`
   - `pending_tasks_total`

## 🔧 Configuration

### Adjust Retry Settings
Edit `docker-compose.yml` under `environment`:

```yaml
environment:
  - MAX_RETRIES=3              # Max retry attempts
  - INITIAL_RETRY_DELAY=5      # Initial wait (seconds)
  - RETRY_BACKOFF_MULTIPLIER=2 # Exponential backoff
  - MAX_RETRY_DELAY=3600       # Max wait (1 hour)
```

### Adjust Prometheus Scrape Interval
Edit `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s  # Change this
```

## 📈 Key Metrics to Monitor

1. **Task Submissions** - New tasks coming in
2. **Task Completions** - Successfully processed tasks
3. **Task Duration** - Processing time per task
4. **Retry Attempts** - Failed tasks being retried
5. **DLQ Size** - Failed tasks after max retries
6. **Active Workers** - How many workers are processing
7. **Pending Tasks** - Backlog in queue

## 🧪 Run Stress Test with Monitoring

```bash
# Terminal 1: Start monitoring
watch 'curl -s http://localhost:8000/health | python -m json.tool'

# Terminal 2: Run stress test
python tests/stress_test.py

# Terminal 3: Watch worker processing
docker logs -f task-queue-worker-1 | grep -E "ASSIGNED|COMPLETED|RETRYING"
```

## 📋 Example Workflows

### Workflow 1: Process Bulk Tasks
```bash
# Submit 100 tasks
for i in {1..100}; do
  curl -s -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"type":"process","data":"item-'$i'"}' > /dev/null
done

# Monitor progress
watch 'curl -s http://localhost:8000/health | python -m json.tool'

# View in dashboard: http://localhost:5001
```

### Workflow 2: Handle Failures with Retries
```bash
# Submit task
TASK_ID=$(curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"calculate","data":999}' | jq -r '.task_id')

# Monitor task status
watch "curl -s http://localhost:8000/tasks/$TASK_ID | python -m json.tool"

# After max retries, check DLQ
curl http://localhost:8000/dlq/failed-tasks

# Retry from DLQ
curl -X POST http://localhost:8000/dlq/failed-tasks/$TASK_ID/retry
```

### Workflow 3: Analyze Performance
```bash
# 1. Get metrics in Prometheus format
curl http://localhost:8000/metrics

# 2. View graphs in Prometheus
# http://localhost:9090

# 3. Check traces in Jaeger
# http://localhost:16686

# 4. See live stats in Dashboard
# http://localhost:5001
```

## 🛑 Stopping Services

```bash
# Stop all containers but keep data
docker-compose stop

# Stop and remove everything
docker-compose down

# Stop and remove including volumes
docker-compose down -v
```

## 🔍 Troubleshooting

### Dashboard not loading?
```bash
docker logs task-queue-dashboard
```

### No metrics showing?
```bash
# Check gateway is running
curl http://localhost:8000/health

# Check metrics endpoint
curl http://localhost:8000/metrics
```

### Jaeger shows no traces?
```bash
# Verify Jaeger is running
docker logs task-queue-jaeger

# Submit a task and check traces
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"process","data":"test"}'

# Wait a few seconds then check Jaeger
```

### Tasks stuck in retry?
```bash
# Check retry queue
redis-cli ZRANGE tasks:retry 0 -1

# View task details
redis-cli GET 'task:{TASK_ID}'

# Manual retry from DLQ
curl -X POST http://localhost:8000/dlq/failed-tasks/{TASK_ID}/retry
```

## 📚 Next Steps

1. **Customize Dashboard**: Modify HTML/CSS in `src/dashboard/templates/index.html`
2. **Add Custom Metrics**: Edit `src/shared/metrics.py`
3. **Adjust Timeouts**: Update worker execution time in `src/worker/worker.py`
4. **Scale Workers**: Change `replicas` in `docker-compose.yml`
5. **Deploy to K8s**: Use manifests in `k8s/deployment.yaml`

## 📖 Documentation

- Full features: See [ADVANCED_FEATURES.md](./ADVANCED_FEATURES.md)
- API docs: Check gateway logs or use http://localhost:8000
- Kubernetes setup: See [k8s/deployment.yaml](./k8s/deployment.yaml)

## 💡 Tips & Tricks

1. **View all tasks**: `redis-cli SCAN 0 MATCH "task:*"`
2. **Clear DLQ**: `redis-cli DEL dlq:failed_tasks`
3. **Reset metrics**: `docker restart task-queue-gateway`
4. **Export metrics**: `curl http://localhost:8000/metrics > metrics.txt`
5. **Check worker capacity**: `docker logs task-queue-worker-1 | wc -l`

Enjoy! 🚀
