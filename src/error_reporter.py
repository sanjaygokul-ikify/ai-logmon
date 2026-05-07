import logging
from loguru import logger

class ErrorReporter:
    def __init__(self):
        self.logger = logger

    def start(self):
        self.logger.info('Error reporter started')
        # Error reporting logic goes here
    