from loguru import logger


class ModelTrainingLogger:
    def __init__(self):
        self.logger = logger

    def start(self):
        self.logger.info('Model training logger started')
        # Model training logging logic goes here

    def log_epoch(self, epoch, metrics):
        self.logger.info(f'Epoch {epoch} completed: {metrics}')

    def log_metrics(self, metrics):
        self.logger.info(f'Training metrics: {metrics}')