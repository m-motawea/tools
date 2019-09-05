import logging


class Logger(object):
    def __init__(self, path="./"):
        self.stream_logger, self.info_logger, self.error_logger, self.debug_logger = self.initialize_logger(path)
​
    def initialize_logger(self, path="./"):
        error_logger = logging.getLogger("BUCKET_MIGRATION_ERROR")
        info_logger = logging.getLogger("BUCKET_MIGRATION_INFO")
        debug_logger = logging.getLogger("BUCKET_MIGRATION_DEBUG")
        stream_logger = logging.getLogger("BUCKET_MIGRATION_STREAM")
        stream_handler = logging.StreamHandler()
        error_handler = logging.FileHandler(path + 'error.log')
        info_handler = logging.FileHandler(path + 'info.log')
        debug_handler = logging.FileHandler(path + 'debug.log')
​
        stream_handler.setLevel(logging.INFO)
        error_handler.setLevel(logging.ERROR)
        info_handler.setLevel(logging.INFO)
        debug_handler.setLevel(logging.DEBUG)
​
        # set format
        stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(stream_format)
        error_handler.setFormatter(file_format)
        info_handler.setFormatter(file_format)
        debug_handler.setFormatter(file_format)
​
        # register handlers
        stream_logger.addHandler(stream_handler)
        error_logger.addHandler(error_handler)
        info_logger.addHandler(info_handler)
        debug_logger.addHandler(debug_handler)
        stream_logger.setLevel(logging.INFO)
        error_logger.setLevel(logging.ERROR)
        info_logger.setLevel(logging.INFO)
        debug_logger.setLevel(logging.DEBUG)
​
        return stream_logger, info_logger, error_logger, debug_logger
​
    def INFO(self, message):
        self.stream_logger.info(message)
        self.info_logger.info(message)
​
    def ERROR(self, message):
        self.stream_logger.error(message)
        self.error_logger.error(message)
        self.debug_logger.error(message)
​
    def DEBUG(self, message):
        self.debug_logger.debug(message)
​
