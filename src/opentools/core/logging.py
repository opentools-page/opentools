import logging


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03dZ | %(levelname)s | %(name)s | %(filename)s (line %(lineno)d) | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    return logging.getLogger(name)
