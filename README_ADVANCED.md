# Distributed Task Queue - Advanced Implementation

## 📋 Overview

This is a **production-ready distributed task queue system** built with Python, Redis, and Kubernetes. It includes enterprise-grade features for reliability, observability, and monitoring.

## ✨ Key Features

### Core Features
- ✅ **Distributed Task Processing** - Multiple workers processing tasks in parallel
- ✅ **Task Retry with Exponential Backoff** - Automatic retries with configurable delays
- ✅ **Dead Letter Queue (DLQ)** - Failed tasks moved to DLQ for manual handling
- ✅ **Task Priority** - High and normal priority task queues
- ✅ **Prometheus Metrics** - Comprehensive metrics for monitoring
- ✅ **Jaeger Distributed Tracing** - End-to-end request tracing
- ✅ **Web Dashboard** - Real-time monitoring interface
- ✅ **Kubernetes Ready** - Production deployment manifests included
- ✅ **Enhanced Logging** - Visual task tracking with emojis

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- kubectl (for Kubernetes deployment)

### Start in 30 seconds
```bash
# Clone and navigate
cd distributed-task-queue-python

# Start all services
docker-compose up -d --build

# Open dashboard
open http://localhost:5001
```

### Services Available
- **Gateway API** - http://localhost:8000
- **Dashboard** - http://localhost:5001
- **Prometheus** - http://localhost:9090
- **Jaeger** - http://localhost:16686

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [FEATURES_SUMMARY.md](./FEATURES_SUMMARY.md) | Complete feature overview |
| [ADVANCED_FEATURES.md](./ADVANCED_FEATURES.md) | Detailed feature documentation & deployment |
| [QUICK_START_FEATURES.md](./QUICK_START_FEATURES.md) | Quick start guide with examples |
| [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md) | CLI commands & cheat sheet |

## 🎯 What's Implemented

### 1. Task Retry with Exponential Backoff
Failed tasks automatically retry with increasing delays:
- Initial delay: 5 seconds (configurable)
- Backoff multiplier: 2.0x (configurable)
- Max delay: 1 hour (configurable)
- Max retries: 3 (configurable)

```python
# Configure in docker-compose.yml
MAX_RETRIES=3
INITIAL_RETRY_DELAY=5
RETRY_BACKOFF_MULTIPLIER=2.0
MAX_RETRY_DELAY=3600
```

### 2. Dead Letter Queue
Tasks that fail after max retries go to DLQ for analysis and manual retry:

```bash
# View failed tasks
curl http://localhost:8000/dlq/failed-tasks

# Retry a failed task
curl -X POST http://localhost:8000/dlq/failed-tasks/{TASK_ID}/retry

# Remove from DLQ
curl -X DELETE http://localhost:8000/dlq/failed-tasks/{TASK_ID}
```

### 3. Prometheus Metrics
Comprehensive metrics tracking all operations:
- Task submissions/completions/failures
- Processing duration
- Retry attempts
- Queue sizes
- Worker status
- DLQ size

Access: http://localhost:8000/metrics

### 4. Jaeger Distributed Tracing
Full request tracing across all services:
- Request flow visualization
- Operation timing
- Error tracking
- Redis operation tracing

Access: http://localhost:16686

### 5. Web Dashboard
Real-time monitoring interface showing:
- Live statistics
- Active workers
- Recent tasks
- Dead Letter Queue
- Auto-refresh every 5 seconds

Access: http://localhost:5001

### 6. Kubernetes Deployment
Complete K8s manifests for production:
- Redis with persistent storage
- Gateway with load balancer
- Multiple workers with scaling
- Prometheus & Jaeger for monitoring
- Dashboard for visualization

Deploy: `kubectl apply -f k8s/deployment.yaml`

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Client Applications                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │Gateway │  │Metrics │  │Dashboard │
    │:8000   │  │:8000   │  │:5001     │
    └────┬───┘  └───┬────┘  └────┬─────┘
         │          │            │
         └──────────┼────────────┘
                    │
          ┌─────────▼──────────┐
          │      Redis         │
          │ (Queues, Storage)  │
          └────┬───────┬───┬───┘
               │       │   │
         ┌─────┘       │   └──────────┐
         │             │              │
    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
    │ Worker1 │  │ Worker2 │  │ Worker3 │
    └─────────┘  └─────────┘  └─────────┘

┌─────────────┐      ┌──────────┐
│ Prometheus  │      │  Jaeger  │
│  Metrics    │      │ Tracing  │
│  :9090      │      │  :16686  │
└─────────────┘      └──────────┘
```

## 🔄 Task Lifecycle

```
1. SUBMIT      → Task submitted via API
                 📤 SUBMITTED log message
                 Stored in Redis
                 Added to pending queue

2. ASSIGN      → Worker picks up task
                 📋 ASSIGNED log message
                 Status → "processing"

3. PROCESS     → Task is executing
                 ⚙️ STARTED log message
                 ⏱️ Simulated processing
                 
4. COMPLETE    → Task finished
                 ✅ COMPLETED log message
                 Status → "completed"
                 OR
4. FAIL        → Task failed
                 ❌ ERROR log message
                 Status → "retrying"
                 Scheduled for retry
                 
5. RETRY       → Retry after delay
                 🔄 REQUEUED log message
                 Status → "pending"
                 (repeats from step 2)
                 
6. DLQ         → Max retries exhausted
                 💀 DLQ log message
                 Status → "failed"
                 Stored in Dead Letter Queue
```

## 💻 Usage Examples

### Submit a Task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "process",
    "data": "hello-world",
    "priority": "high"
  }'
```

### Get Task Status
```bash
curl http://localhost:8000/tasks/{TASK_ID}
```

### Monitor System Health
```bash
curl http://localhost:8000/health
```

### View Metrics
```bash
# Raw Prometheus format
curl http://localhost:8000/metrics

# In Prometheus UI
open http://localhost:9090
# Query: task_submissions_total
```

### Trace Requests
```bash
open http://localhost:16686
# Select service: "gateway"
# View traces showing request flow
```

### Run Stress Test
```bash
python tests/stress_test.py
# Submits 100 tasks and monitors completion
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MAX_RETRIES` | 3 | Maximum retry attempts |
| `INITIAL_RETRY_DELAY` | 5 | Initial retry delay (seconds) |
| `RETRY_BACKOFF_MULTIPLIER` | 2.0 | Backoff multiplier per retry |
| `MAX_RETRY_DELAY` | 3600 | Maximum retry delay (seconds) |
| `REDIS_HOST` | localhost | Redis server hostname |
| `REDIS_PORT` | 6379 | Redis server port |
| `JAEGER_HOST` | localhost | Jaeger agent hostname |
| `JAEGER_PORT` | 6831 | Jaeger agent port |

### Customize Retry Strategy
Edit `docker-compose.yml`:
```yaml
environment:
  - MAX_RETRIES=5
  - INITIAL_RETRY_DELAY=10
  - RETRY_BACKOFF_MULTIPLIER=1.5
  - MAX_RETRY_DELAY=7200
```

## 📈 Monitoring

### Prometheus Metrics
- `task_submissions_total` - Total tasks submitted
- `task_completions_total` - Completed tasks
- `task_duration_seconds` - Processing time (histogram)
- `task_retries_total` - Total retries
- `tasks_in_dlq_total` - Failed tasks
- `active_workers_total` - Active workers
- `pending_tasks_total` - Pending tasks

### Jaeger Traces
- Request flow visualization
- Service dependencies
- Operation timing
- Error tracking
- Redis operation tracing

### Dashboard Metrics
- Real-time task counts
- Worker status
- Queue depths
- DLQ management

## 🚀 Deployment

### Docker Compose (Development/Testing)
```bash
docker-compose up -d --build
```

### Kubernetes (Production)
```bash
# Apply all manifests
kubectl apply -f k8s/deployment.yaml

# Scale workers
kubectl scale deployment worker -n task-queue --replicas=5

# Port forward services
kubectl port-forward -n task-queue svc/gateway 8000:5000
kubectl port-forward -n task-queue svc/dashboard 5001:5001
```

## 🔍 Troubleshooting

### Services not starting?
```bash
# Check logs
docker logs task-queue-gateway
docker logs task-queue-worker-1

# Verify Redis
redis-cli PING
```

### Metrics not appearing?
```bash
# Verify endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
open http://localhost:9090/targets
```

### Tasks not processing?
```bash
# Check worker logs
docker logs -f task-queue-worker-1

# Check queue status
curl http://localhost:8000/health

# Verify Redis
redis-cli LLEN tasks:pending
```

## 📁 Project Structure

```
distributed-task-queue-python/
├── src/
│   ├── gateway/
│   │   └── server.py              # REST API gateway
│   ├── worker/
│   │   └── worker.py              # Task worker with retry logic
│   ├── dashboard/
│   │   ├── app.py                 # Dashboard API
│   │   └── templates/index.html   # Dashboard UI
│   └── shared/
│       ├── metrics.py             # Prometheus metrics
│       └── tracing.py             # Jaeger tracing
├── k8s/
│   └── deployment.yaml            # Kubernetes manifests
├── tests/
│   ├── stress_test.py             # Load test
│   └── test_client.py             # Interactive CLI client
├── docker-compose.yml             # Docker Compose config
├── Dockerfile.*                   # Container definitions
├── prometheus.yml                 # Prometheus config
├── requirements.txt               # Python dependencies
└── *.md                           # Documentation files
```

## 📚 Additional Resources

### Documentation Files
- **FEATURES_SUMMARY.md** - Complete feature overview
- **ADVANCED_FEATURES.md** - Detailed deployment guide
- **QUICK_START_FEATURES.md** - Quick examples
- **COMMAND_REFERENCE.md** - CLI command cheat sheet

### Key Files
- **docker-compose.yml** - Full stack configuration
- **k8s/deployment.yaml** - Kubernetes manifests
- **prometheus.yml** - Prometheus configuration

## 🎯 Next Steps

1. **Explore the Dashboard**
   - Open http://localhost:5001
   - Submit some tasks
   - Monitor in real-time

2. **Check the Metrics**
   - Open http://localhost:9090
   - Query task_submissions_total
   - View graphs

3. **Trace a Request**
   - Open http://localhost:16686
   - Select "gateway" service
   - Click "Find Traces"

4. **Run Stress Test**
   - `python tests/stress_test.py`
   - Watch workers process 100 tasks

5. **Deploy to Kubernetes**
   - Build images for your cluster
   - `kubectl apply -f k8s/deployment.yaml`
   - Scale workers as needed

## 🤝 Contributing

Feel free to extend this system with:
- Custom task types
- Additional metrics
- Custom dashboard widgets
- Integration with other systems

## 📝 License

This project is provided as-is for educational and production use.

---

**Last Updated:** December 24, 2025

**Status:** ✅ All Features Implemented & Tested

For detailed information, see the documentation files listed above.
