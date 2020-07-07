#!/usr/bin/env python3

import os
import smbus2
import bme280

class BME280():
    def __init__(self, address):
        port = 1
        if not os.path.isfile("/dev/i2c-{0}".format(port)):
            raise RuntimeError('failed detect i2c device')

        self.address = address
        self.bus = smbus2.SMBus(port)

        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)


    def get(self):
        try:
            data = bme280.sample(self.bus, self.address, self.calibration_params)
            return {
                'temp': data.temperature,
                'pressure': data.pressure,
                'humid': data.humidity
            }

        except Exception as ex:
            raise RuntimeError("failed get from BME")
