import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram

REQUESTS = Counter("c4l_requests", "Authenticated agent requests", ["outcome"])
LATENCY = Histogram("c4l_latency_seconds", "Agent latency", buckets=(0.1, 0.5, 1, 2, 5, 10, 15, 30))
COST = Counter("c4l_cost_usd", "Reported agent cost; excludes failed or timed-out unknown usage")
UNKNOWN = Counter("c4l_unknown_usage", "Requests with potentially unreported usage")


def setup():
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return
    provider = TracerProvider(resource=Resource.create({"service.name": "c4l-agent-api"}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
