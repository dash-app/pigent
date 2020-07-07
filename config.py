#!/usr/bin/env python3
import os
http_port = os.getenv("PIGENT_HTTP_PORT", default=8081)
ir_gpio = os.getenv("PIGENT_IR_GPIO", default=4)
bme280_address = os.getenv("BME280_ADDRESS", default=0x76)
debug = os.getenv("DEBUG", default=None)
