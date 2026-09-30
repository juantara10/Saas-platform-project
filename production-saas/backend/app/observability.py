from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.core.config import settings
def setup(app):
 if settings.otel_exporter_otlp_endpoint:
  provider=TracerProvider(); provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint,insecure=True))); trace.set_tracer_provider(provider)
 FastAPIInstrumentor.instrument_app(app)
