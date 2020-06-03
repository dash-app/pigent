#!/usr/bin/env python3

import sys
import os
import logging
import config
import web

# Logging
LOG_LEVEL = logging.INFO
if os.getenv("DEBUG", "") != "":
    LOG_LEVEL = logging.DEBUG

logging.basicConfig(
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S %z',
        level=LOG_LEVEL
)

logging.info("Starting Pigent...")

# Start web API
web.start(config)
