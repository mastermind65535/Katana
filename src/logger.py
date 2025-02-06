import logging

def setup_logger():
    LOG = logging.getLogger("Katana")
    LOG.setLevel(logging.INFO)

    CONSOLE_LOGGER = logging.StreamHandler()
    CONSOLE_LOGGER.setLevel(logging.DEBUG)
    CONSOLE_LOGGER.setFormatter(logging.Formatter('%(message)s'))

    LOG.addHandler(CONSOLE_LOGGER)

    return LOG

LOGGER = setup_logger()