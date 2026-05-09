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
        }

        if record.exc_info:
            log_data["traceback"] = traceback.format_exception(*record.exc_info)
    
        return json.dumps(log_data)