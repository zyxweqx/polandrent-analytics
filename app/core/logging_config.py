import logging


def setup_logging(lvl: int = logging.INFO):
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s %(levelname)s %(name)s:  %(message)s",
    )