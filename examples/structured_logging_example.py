from src.logging.json_logger import StructuredLogger


logger = StructuredLogger()

logger.log_inference_start(
    model_name="llama3",
    request_id="req-123",
)

logger.log_inference_end(
    model_name="llama3",
    request_id="req-123",
    latency_ms=145,
    token_count=512,
)