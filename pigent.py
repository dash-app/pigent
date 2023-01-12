#!/usr/bin/env python3
import sys
import logging
import config
import web
import traceback

# Logging
LOG_LEVEL = logging.INFO if not config.debug else logging.DEBUG
logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S %z',
    level=LOG_LEVEL
)

# Start web API
try:
    logging.info("Starting Pigent...")

    if config.debug:
        logging.warning("==============================")
        logging.warning("WARNING: DEBUG MODE IS ENABLED")
        logging.warning(
            "WARNING: SOME APIs(ex. sensors) WILL BE RESPOND AS DUMMY!!!")
        logging.warning("==============================")

    web.start(config)
except Exception as ex:
    logging.critical(f"Failed start pigent: {ex}")
    print(traceback.format_exc())
    sys.exit(1)
