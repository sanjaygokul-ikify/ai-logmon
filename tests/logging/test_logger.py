from src.logging.json_logger import StructuredLogger


def test_structured_logger_initialization():
    logger = StructuredLogger()

    assert logger is not None
    assert logger.logger is not None


def test_structured_logger_info_method():
    logger = StructuredLogger()

    logger.info(
        "Test structured log",
        model_name="llama3",
        latency_ms=120,
    )

    assert True