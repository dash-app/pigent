#!/usr/bin/env python3

import json
import logging
import tornado.ioloop
import tornado.web

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        raise tornado.web.HTTPError(status_code=404, reason="Not Found")

    def write_error(self, status_code, exc_info=None, **kwargs):
        self.finish({"error": self._reason})


def start(config):
    web = tornado.web.Application([
    ], default_handler_class=DefaultHandler)

    web.listen(config.http_port)
    logging.info("HTTP Server started on %d", int(config.http_port))

    tornado.ioloop.IOLoop.current().start()
