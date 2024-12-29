# logging_conf.py
import logging

def setup_logging(level=logging.INFO):
    """
    Configure the global logging.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # You can customize further if needed, 
    # or add a file handler, etc.