# src/shared/metrics.py
"""
Prometheus metrics for the distributed task queue system
"""

from prometheus_client import Counter, Histogram, Gauge
import time

# Task metrics
task_submissions = Counter(
    'task_submissions_total',
    'Total number of task submissions',
    ['priority', 'task_type']
)

task_completions = Counter(
    'task_completions_total',
    'Total number of completed tasks',
    ['task_type', 'status']
)

task_duration = Histogram(
    'task_duration_seconds',
    'Task processing duration in seconds',
    ['task_type']
)

task_retries = Counter(
    'task_retries_total',
    'Total number of task retries',
    ['task_type', 'retry_count']
)

tasks_in_dlq = Gauge(
    'tasks_in_dlq_total',
    'Number of tasks in the dead letter queue'
)

# Worker metrics
active_workers = Gauge(
    'active_workers_total',
    'Number of active workers'
)

worker_tasks_processed = Counter(
    'worker_tasks_processed_total',
    'Total tasks processed by each worker',
    ['worker_id']
)

# Queue metrics
pending_tasks = Gauge(
    'pending_tasks_total',
    'Number of pending tasks',
    ['priority']
)

retry_tasks = Gauge(
    'retry_tasks_total',
    'Number of tasks scheduled for retry'
)

# Error metrics
task_failures = Counter(
    'task_failures_total',
    'Total number of task failures',
    ['task_type', 'error_type']
)

worker_errors = Counter(
    'worker_errors_total',
    'Total number of worker errors',
    ['worker_id', 'error_type']
)
