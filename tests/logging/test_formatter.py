import json
import logging

from src.logging.formatters import JsonFormatter


def test_json_formatter_output():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test log message",
        args=(),
        exc_info=None,
    )

    output = formatter.format(record)
    log_data = json.loads(output)

    assert log_data["message"] == "Test log message"
    assert log_data["level"] == "INFO"