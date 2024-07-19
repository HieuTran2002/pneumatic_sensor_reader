import logging
import logging.handlers
from sys import stdout


class Logger:
    def __init__(self, log_file="message.log", max_bytes=30720, backup_count=10):
        self.log_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.log_handler = logging.handlers.RotatingFileHandler(
            log_file,
            mode="a",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        self.log_handler.setFormatter(self.log_formatter)
        self.stream_log = logging.StreamHandler(stdout)
        self.stream_log.setFormatter(self.log_formatter)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)  # Set the default level to DEBUG
        self.logger.addHandler(self.log_handler)
        self.logger.addHandler(self.stream_log)

    def log(self, level, message):
        if level == "debug":
            self.logger.debug(message)
        elif level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)
        else:
            raise ValueError(f"Unsupported logging level: {level}")


if __name__ == "__main__":
    my_logger = Logger()
    print('hellow')
    my_logger.log("debug", "This is a Debug Message")
    my_logger.log("info", "This is an Info Message")
    my_logger.log("warning", "This is a Warning Message")
    my_logger.log("error", "This is an Error Message")
    my_logger.log("critical", "This is a Critical Message")    
