import logging
import logging.handlers as handlers
import os
import time
import sys


class Logger():

    log_dir = ""
    logger = ""

    def __init__(self):

        self._create_log_directory()
        log_filename = os.path.join(self.log_dir, "Endo_Analysis.log")
        logHandler = handlers.RotatingFileHandler(log_filename, maxBytes=1000000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logHandler.setFormatter(formatter)
        self.logger = logging.getLogger("Endo_Analysis")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logHandler)

    def _create_log_directory(self):

        self.log_dir = os.path.join(os.getcwd(), "logs")

        # ONLY CREATE THE DIRECTORY THE FIRST TIME THE APP RUNS
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log(self, message, exception):

        self.logger.info(message)

        if exception:
            self.logger.exception(exception)

