import time
from functools import wraps
from loguru import logger


# --- Decorators ---
def singleton(cls):
    instances = {}
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logger.info(f"Function '{func.__name__}' executed in {end_time - start_time:.4f}s")
        return result
    return wrapper


def log_details(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling function '{func.__name__}'")
        logger.info(f"Arguments: {args}")
        logger.info(f"Keyword Arguments: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function '{func.__name__}' returned: {result}")
            return result
        except Exception:
            logger.exception(f"Function '{func.__name__}' raised an exception")
            raise
    return wrapper
