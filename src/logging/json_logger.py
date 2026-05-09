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