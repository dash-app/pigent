#!/usr/bin/env python3

import json
import logging
import tornado.ioloop
import tornado.web
from util import ir
from sensors import bme

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        raise tornado.web.HTTPError(status_code=404, reason="Not Found")

    def write_error(self, status_code, exc_info=None, **kwargs):
        self.finish({"error": self._reason})

# /api/v1/ir
class IRHandler(tornado.web.RequestHandler):
    def initialize(self, config):
        self.config = config

    def post(self):
        try:
            req = tornado.escape.json_decode(self.request.body)
            signal = req['code']
            ir.send(self.config.ir_gpio, signal)

            self.write({"status": "success"})
        except json.decoder.JSONDecodeError as ex:
            raise tornado.web.HTTPError(status_code=400, reason="failed decode json")
        except RuntimeError as ex:
            raise tornado.web.HTTPError(status_code=500, reason=str(ex))

    def write_error(self, status_code, exc_info=None, **kwargs):
        self.finish({"error": self._reason})

# /api/v1/sensors
class SensorsHandler(tornado.web.RequestHandler):
    def initialize(self, config, sensors):
        self.config = config
        self.sensors = sensors

    def get(self):
        if self.config.debug is not None:
            self.write(self.sensors.example())
            return

        try:
            r = self.sensors.get()
            self.write(r)
        except RuntimeError as ex:
            raise tornado.web.HTTPError(status_code=500, reason=str(ex))
    def write_error(self, status_code, exc_info=None, **kwargs):
        self.finish({"error": self._reason})

def start(config):
    try:
        sensors = bme.BME280(config.bme280_address, config.debug)
        web = tornado.web.Application([
            (r"/api/v1/ir", IRHandler, dict(config=config)),
            (r"/api/v1/sensors", SensorsHandler, dict(config=config, sensors=sensors))
        ], default_handler_class=DefaultHandler)

        # Enable no_keep_alive (Causes of 'Too many open files' Problem)
        server = tornado.httpserver.HTTPServer(web)
        server.listen(config.http_port)
        logging.info("HTTP Server started on %d", int(config.http_port))

        tornado.ioloop.IOLoop.instance().start()
    except RuntimeError as ex:
        logging.error("Initialize error: %s", str(ex))
        raise ex
