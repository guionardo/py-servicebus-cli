import logging

logging.basicConfig(format=logging.BASIC_FORMAT,
                    handlers=[logging.StreamHandler()],
                    level=logging.DEBUG)

logging.getLogger(__name__).info('TESTING LOGGING ENABLED')
