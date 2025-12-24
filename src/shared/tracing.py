# src/shared/tracing.py
"""
Distributed tracing setup using OpenTelemetry and Jaeger
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
import os

def init_tracing(service_name='task-queue-service'):
    """Initialize OpenTelemetry tracing with Jaeger exporter"""
    
    # Get Jaeger configuration from environment
    jaeger_host = os.getenv('JAEGER_HOST', 'localhost')
    jaeger_port = int(os.getenv('JAEGER_PORT', 6831))
    
    # Create Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    
    # Set the tracer provider
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # Instrument libraries
    FlaskInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()
    
    print(f"[Tracing] Initialized Jaeger tracing for {service_name}")

def get_tracer(module_name):
    """Get a tracer instance for a specific module"""
    return trace.get_tracer(module_name)
