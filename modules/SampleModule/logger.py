import logging

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

class Logger(object):
    def __init__(self, format=FORMAT, level=logging.DEBUG, name=__name__):
        logging.basicConfig(format=format, level=level)

        self.logger = logging.getLogger(name)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def exception(self, msg):
        self.logger.exception(msg)

    def critical(self, msg):
        self.logger.critical(msg)


logger = Logger()