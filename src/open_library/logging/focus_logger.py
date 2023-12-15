#!/usr/bin/env python3
import logging
import logging.config

# Placeholder for original logger settings
original_settings = {}

# Define a special handler for your focused logger
special_handler = logging.StreamHandler()
special_file_handler = logging.FileHandler("other_logs.txt", mode="a")

# Create your special logger
focus_logger = logging.getLogger("focus-logger")
focus_logger.addHandler(special_handler)
focus_logger.setLevel(logging.DEBUG)

def activate_special_mode():
    # Iterate over all loggers
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(
            logger, logging.Logger
        ):  # Ensures it's actually a logger and not a placeholder
            # Store original settings for later restoration
            original_settings[name] = {
                "level": logger.level,
                "handlers": logger.handlers.copy(),
            }

            # Modify logger
            logger.handlers = [special_file_handler]
            logger.setLevel(logging.INFO)


def deactivate_special_mode():
    # Restore original settings
    for name, logger in logging.Logger.manager.loggerDict.items():
        if name in original_settings:
            logger.handlers = original_settings[name]["handlers"]
            logger.setLevel(original_settings[name]["level"])

# DEBUG < INFO < WARNING < ERROR < CRITICAL

if __name__ == "__main__":
    # Testing
    logging.getLogger("module1").debug("This should appear in console.")
    logging.getLogger("module2").debug("This should appear in console too.")
    focus_logger.debug("This is from the focus logger to console.")

    activate_special_mode()
    logging.getLogger("module1").debug("This will not appear due to raised level.")
    logging.getLogger("module2").info("This will be written to 'other_logs.txt'.")
    focus_logger.debug("This is still from the focus logger to console.")

    deactivate_special_mode()
    logging.getLogger("module1").debug("This should appear in console again.")
    logging.getLogger("module2").debug("This should appear in console again too.")
