from .config import setup_logger


class StructuredLogger:
    def __init__(self, name="ai-logmon"):
        self.logger = setup_logger(name)

    def info(self, message, **kwargs):
        self.logger.info(message, extra=kwargs)

    def error(self, message, **kwargs):
        self.logger.error(message, extra=kwargs)

    def warning(self, message, **kwargs):
        self.logger.warning(message, extra=kwargs)
        
        def log_inference_start(self, model_name, request_id):
        self.info(
            "Inference started",
            model_name=model_name,
            request_id=request_id,
        )

    def log_inference_end(
        self,
        model_name,
        request_id,
        latency_ms,
        token_count=None,
    ):
        self.info(
            "Inference completed",
            model_name=model_name,
            request_id=request_id,
            latency_ms=latency_ms,
            token_count=token_count,
        )

    def log_inference_error(
        self,
        model_name,
        request_id,
        error_message,
    ):
        self.error(
            error_message,
            model_name=model_name,
            request_id=request_id,
        )