import logging

from datetime import date

__IS_INITIALIZED = False
__LOG_FILE_NAME = f'{date.today()}.log'
__LOGGING_FORMAT = '%(name)-12s %(levelname)-8s %(message)s'
__LOG_DEFAULT_LEVEL = logging.INFO


def __init_logger():
    global __IS_INITIALIZED
    if __IS_INITIALIZED:
        return

    # ref: https://docs.python.org/3/howto/logging-cookbook.html#logging-to-multiple-destinations
    # First set the root logger to log to a file
    logging.basicConfig(
        level=__LOG_DEFAULT_LEVEL,
        format='%(asctime)s ' + __LOGGING_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=__LOG_FILE_NAME, # default to append mode
    )

    # Add handler to stderr
    console = logging.StreamHandler()
    # simplify logging (compare to the file log)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(__LOGGING_FORMAT))

    root_logger = logging.getLogger('')
    root_logger.addHandler(console)
    __IS_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def is_time_to_log(
        current_iteration: int,
        total_count: int,
        percentile: int = 20) -> bool:
    """A function to be used to check the periodic logging time.

    It returns true if current_iteration is at specific percentile in progress.

    Args:
        current_iteration (int): a number to represent current iteration (count from 1)
        total_count (int): the total number of iterations to run
        percentile (int, optional): a percentile to notify. Defaults to 20(%).

    Returns:
        bool: true if current_iteration is at specific percentile. If percentile is not in the right range, false would
            be always returned.
    """
    if not 1 <= percentile <= 100:
        return False

    denominator = int(total_count * (percentile / 100))
    if denominator == 0:
        return False
    else:
        return current_iteration % denominator == 0


__init_logger()
