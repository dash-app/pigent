import os

http_port = os.getenv("PIGENT_HTTP_PORT", default=8081)
ir_gpio = int(os.getenv("PIGENT_IR_GPIO", default=4))

# find from : i2cdetect -y 1
bme280_address = int(os.getenv("BME280_ADDRESS", default="0x76"), 0)

debug = os.getenv("DEBUG", default=None)
