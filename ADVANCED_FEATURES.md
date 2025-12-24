# Advanced Deployment Guide

This guide covers all the advanced features implemented in the distributed task queue system.

## Features Implemented

### 1. Task Retry with Exponential Backoff
- Automatic retry mechanism for failed tasks
- Configurable maximum retries (default: 3)
- Exponential backoff strategy with configurable multiplier
- Failed tasks move to Dead Letter Queue after max retries

**Configuration Environment Variables:**
```
MAX_RETRIES=3
INITIAL_RETRY_DELAY=5  # seconds
RETRY_BACKOFF_MULTIPLIER=2.0
MAX_RETRY_DELAY=3600  # 1 hour
```

**How it works:**
1. Task fails → retry scheduled with delay of INITIAL_RETRY_DELAY
2. Second failure → delay = INITIAL_RETRY_DELAY * 2.0 = 10 seconds
3. Third failure → delay = INITIAL_RETRY_DELAY * 2.0^2 = 20 seconds
4. After MAX_RETRIES exhausted → task moved to DLQ

### 2. Dead Letter Queue (DLQ)
- Tasks that exceed max retries are moved to DLQ
- API endpoints for DLQ management:
  - `GET /dlq/failed-tasks` - List all failed tasks
  - `DELETE /dlq/failed-tasks/<task_id>` - Remove from DLQ
  - `POST /dlq/failed-tasks/<task_id>/retry` - Retry a DLQ task

**Example:**
```bash
# Get all failed tasks
curl http://localhost:8000/dlq/failed-tasks

# Retry a specific task
curl -X POST http://localhost:8000/dlq/failed-tasks/{TASK_ID}/retry
```

### 3. Prometheus Metrics & Observability
- Comprehensive metrics collection for all operations
- Metrics endpoint: `GET http://localhost:8000/metrics`
- Prometheus UI: `http://localhost:9090`

**Available Metrics:**
- `task_submissions_total` - Total task submissions (by priority, type)
- `task_completions_total` - Total completed tasks (by type, status)
- `task_duration_seconds` - Task processing duration histogram
- `task_retries_total` - Total retry attempts
- `tasks_in_dlq_total` - Current DLQ size
- `active_workers_total` - Active worker count
- `pending_tasks_total` - Pending tasks by priority
- `retry_tasks_total` - Tasks scheduled for retry
- `task_failures_total` - Failures by type and error
- `worker_errors_total` - Worker errors by worker and type

### 4. Distributed Tracing (Jaeger)
- OpenTelemetry integration for distributed tracing
- Jaeger UI: `http://localhost:16686`
- Automatic instrumentation of Flask, Redis, and HTTP requests
- Trace correlation across services

**Configuration:**
```
JAEGER_HOST=localhost
JAEGER_PORT=6831
```

### 5. Web Dashboard
- Real-time monitoring dashboard
- URL: `http://localhost:5001`
- Features:
  - Live statistics (completed, pending, retrying, failed tasks)
  - Active workers list with task counts
  - Recent tasks with status and retry info
  - Dead Letter Queue browser and management
  - Auto-refresh every 5 seconds

### 6. Kubernetes Deployment
- Complete K8s manifests for production deployment
- Includes: Redis, Gateway, Workers, Dashboard, Prometheus, Jaeger
- Resource limits and health checks configured
- Persistent storage for Redis
- Load balancer services for external access

## Docker Compose Setup

### Start all services:
```bash
docker-compose up -d --build
```

### Service URLs:
- Gateway API: `http://localhost:8000`
- Dashboard: `http://localhost:5001`
- Prometheus: `http://localhost:9090`
- Jaeger UI: `http://localhost:16686`
- Metrics: `http://localhost:8000/metrics`

### Stop all services:
```bash
docker-compose down
```

## Kubernetes Setup

### Prerequisites:
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- Docker images built and available

### Deploy to Kubernetes:
```bash
# Create namespace and deploy all manifests
kubectl apply -f k8s/deployment.yaml

# Watch deployment status
kubectl get pods -n task-queue -w

# Port forward services for local access
kubectl port-forward -n task-queue svc/gateway 8000:5000
kubectl port-forward -n task-queue svc/dashboard 5001:5001
kubectl port-forward -n task-queue svc/prometheus 9090:9090
kubectl port-forward -n task-queue svc/jaeger 16686:16686
```

### Verify deployment:
```bash
# Get all resources
kubectl get all -n task-queue

# Check logs
kubectl logs -n task-queue -f deployment/gateway
kubectl logs -n task-queue -f deployment/worker

# Access Prometheus
# http://localhost:9090

# Access Jaeger
# http://localhost:16686

# Access Dashboard
# http://localhost:5001
```

### Scale workers:
```bash
kubectl scale deployment worker -n task-queue --replicas=5
```

## Testing Features

### Test Retry Mechanism:
```bash
# Submit a task that might fail
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "calculate",
    "data": 999,
    "priority": "high"
  }'

# Check task status and retry count
curl http://localhost:8000/tasks/{TASK_ID}

# Monitor retries in logs
docker logs task-queue-worker-1 | grep "🔄"
```

### Monitor Metrics:
```bash
# View raw metrics
curl http://localhost:8000/metrics | grep task_

# View in Prometheus
# http://localhost:9090 -> Graph tab -> search for "task_"
```

### Trace a Request:
```bash
# Make a request
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type": "process", "data": "test"}'

# View trace in Jaeger
# http://localhost:16686 -> Select service -> Gateway -> View traces
```

### Manage Dead Letter Queue:
```bash
# Get DLQ tasks
curl http://localhost:8000/dlq/failed-tasks

# Retry a failed task
curl -X POST http://localhost:8000/dlq/failed-tasks/{TASK_ID}/retry

# Remove from DLQ
curl -X DELETE http://localhost:8000/dlq/failed-tasks/{TASK_ID}
```

## API Reference

### Core API Endpoints:

**Submit Task**
```
POST /tasks
Content-Type: application/json

{
  "type": "process|calculate",
  "data": <any>,
  "priority": "normal|high"
}
```

**Get Task Status**
```
GET /tasks/{TASK_ID}
```

**Get All Tasks**
```
GET /tasks
```

**Health Check**
```
GET /health
```

**List Workers**
```
GET /workers
```

**Metrics**
```
GET /metrics
```

**Dead Letter Queue**
```
GET /dlq/failed-tasks
POST /dlq/failed-tasks/{TASK_ID}/retry
DELETE /dlq/failed-tasks/{TASK_ID}
```

## Performance Tuning

### Redis Configuration:
- Increase `maxmemory` for large task volumes
- Enable persistence with `appendonly yes`
- Use `SCAN` instead of `KEYS` for production

### Worker Configuration:
- Scale workers based on task volume
- Adjust `INITIAL_RETRY_DELAY` for fast retries
- Monitor worker CPU/memory usage

### Dashboard Refresh:
- Default 5-second auto-refresh
- Adjust in HTML for slower connections
- Consider caching for large task counts

## Troubleshooting

### Tasks not processing:
```bash
# Check Redis connection
redis-cli -h localhost PING

# Check worker logs
docker logs task-queue-worker-1

# Verify task in Redis
redis-cli -h localhost GET task:{TASK_ID}
```

### High memory usage:
```bash
# Monitor Redis memory
redis-cli INFO memory

# Clean old tasks if needed
redis-cli SCAN 0 MATCH "task:*"
```

### Metrics not appearing:
```bash
# Verify Prometheus scraping
curl http://localhost:9090/api/v1/targets

# Check gateway metrics endpoint
curl http://localhost:8000/metrics
```

## Production Best Practices

1. **Use persistent Redis**: Deploy with backup strategy
2. **Scale workers**: Based on expected task throughput
3. **Monitor metrics**: Set up alerts in Prometheus
4. **Review DLQ regularly**: Address systematic failures
5. **Configure resource limits**: Prevent resource exhaustion
6. **Enable TLS**: For Prometheus and external connections
7. **Set up logging**: Aggregate logs from all services
8. **Plan for failover**: Use Kubernetes replicas and anti-affinity

## Next Steps

- Integrate with your task management system
- Set up alerting rules in Prometheus
- Create custom dashboards in Grafana
- Implement custom retry strategies
- Add task scheduling (at specific times)
- Implement task dependencies
