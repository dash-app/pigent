#!/usr/bin/env python3

import json
import logging
import tornado.ioloop
import tornado.web
from util import ir

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

def start(config):
    web = tornado.web.Application([
        (r"/api/v1/ir", IRHandler, dict(config=config))
    ], default_handler_class=DefaultHandler)

    web.listen(config.http_port)
    logging.info("HTTP Server started on %d", int(config.http_port))

    tornado.ioloop.IOLoop.current().start()
