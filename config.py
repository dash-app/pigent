#!/usr/bin/env python3
import os
http_port = os.getenv("PIGENT_HTTP_PORT", default=8081)
ir_gpio = os.getenv("PIGENT_IR_GPIO", default=17)
