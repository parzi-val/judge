import logging


def setup_logging():
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(levelname)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    for name in logging.root.manager.loggerDict:
        if not name.startswith("myapp"):
            logging.getLogger(name).setLevel(logging.WARNING)

    logger.propagate = False
