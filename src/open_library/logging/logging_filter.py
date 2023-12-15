#!/usr/bin/env python3
import logging
import time



class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level


class IntervalLoggingFilter(logging.Filter):
    def __init__(self, interval=60):
        super().__init__()
        self.interval = interval
        self.last_logged = 0

    def filter(self, record):
        current_time = time.time()
        if current_time - self.last_logged > self.interval:
            self.last_logged = current_time
            return True
        return False


class WebsocketLoggingFilter(logging.Filter):
    def __init__(self, interval=60):
        super().__init__()
        self.interval = interval
        self.last_logged = 0

    def filter(self, record):
        if ("PING" in record.getMessage() or "PONG" in record.getMessage()) :
            current_time = time.time()
            if current_time - self.last_logged > self.interval:
                self.last_logged = current_time
                return True
            return False
        return True

if __name__ == "__main__":
    # Testing
    # example of max level
    logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
    logger = logging.getLogger(__name__)

    # Add filter to only show DEBUG logs
    handler = logging.StreamHandler()
    handler.addFilter(MaxLevelFilter(logging.DEBUG))
    logger.addHandler(handler)

    logger.debug("This is a debug message.")
    logger.info("This will not be displayed.")


    # Usage
    logger = logging.getLogger('websockets')
    interval_filter = IntervalLoggingFilter(60)  # Log once every 60 seconds
    logger.addFilter(interval_filter)
