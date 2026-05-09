import json
import logging
from datetime import datetime
import traceback

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "inference_id": getattr(record, "inference_id", None),
            "model_name": getattr(record, "model_name", None),
            "latency_ms": getattr(record, "latency_ms", None),
            "token_count": getattr(record, "token_count", None),
        }

        if record.exc_info:
            log_data["traceback"] = traceback.format_exception(*record.exc_info)
    
        return json.dumps(log_data)