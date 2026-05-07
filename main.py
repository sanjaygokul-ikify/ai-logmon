import logging
from ai_logmon.src.log_collector import LogCollector
from ai_logmon.src.log_processor import LogProcessor
from ai_logmon.src.error_reporter import ErrorReporter

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    log_collector = LogCollector()
    log_processor = LogProcessor()
    error_reporter = ErrorReporter()

    log_collector.start()
    log_processor.start()
    error_reporter.start()
    