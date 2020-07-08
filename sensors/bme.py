#!/usr/bin/env python3

import os
import smbus2
import bme280

class BME280():
    def __init__(self, address, debug):
        port = 1
        if debug is None:
            if not os.path.exists("/dev/i2c-{0}".format(port)):
                raise RuntimeError('failed detect i2c device')
        else:
            return
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

    def example(self):
        return {
            'temp': 27.007465454214252,
            'pressure': 1003.5747804753162,
            'humid': 48.63702422735731
        }
