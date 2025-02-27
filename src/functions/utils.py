"""
    File containing utility functions
"""
import os
import logging


def create_logger() -> logging.Logger:
    """
        Create a logger object

        - Args :
            - None

        - Returns :
            - logger (logging.Logger) : the created logger object
    """
    if not os.path.exists('logs'):
        os.makedirs('logs', exist_ok=True)

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('logs/schedule.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug('Logger created successfully')

    return logger


schedule_logger = create_logger()
