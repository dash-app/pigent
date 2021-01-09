#!/usr/bin/env python3

import json
import logging
import tornado.ioloop
import tornado.web
import time
import asyncio
from util import ir, aeha
from sensors import bme
#from switchbot import switchbot

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        raise tornado.web.HTTPError(status_code=404, reason="Not Found")

    def write_error(self, status_code, exc_info=None, **kwargs):
        self.finish({"error": self._reason})



# /api/v1/ir
class IRHandler(tornado.web.RequestHandler):
    def initialize(self, config):
        self.config = config

    async def post(self):
        try:
            req = tornado.escape.json_decode(self.request.body)

            for signal in req:
    
            #    print(signal['signal'])
            #    if 'interval' in signal:
            #        print(signal['interval'])

            #self.write({"status": "success"})
            #return
                #intervalが存在したらそれだけ遅らす
                if 'interval' in signal:
                    print(signal['interval'])
                    await asyncio.sleep(signal['interval']/1000)#500ms->0.5s
                else:
                    print("no")
                if self.config.debug is None:
                    ir.send(self.config.ir_gpio, signal)
                else:
                    arr = [signal['signal'][i:i+2] for i in range(0, len(signal['signal']), 2)]
                    s = aeha.format(arr)
                    fmt = ""
                    for i in range(0, len(s)):
                        fmt += "{ "
                        for j in range(0, len(s[i])):
                            fmt += "0x{:02X} ".format(s[i][j])
                        fmt += "}\n"
                    logging.debug("Received IR Code: \n" + fmt)
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

# /api/v1/switchbot
#class SwitchBotHandler(tornado.web.RequestHandler):
#    def post(self):
#        try:
#            req = tornado.escape.json_decode(self.request.body)
#            mac = req['mac']
#            cmd = req['command']
#            switchbot.run(mac, cmd)
#        except json.decoder.JSONDecodeError as ex:
#            raise tornado.web.HTTPError(status_code=400, reason="failed decode json")
#        except RuntimeError as ex:
#            raise tornado.web.HTTPError(status_code=500, reason=str(ex))

def start(config):
    try:
        sensors = bme.BME280(config.bme280_address, config.debug)
        web = tornado.web.Application([
            (r"/api/v1/ir", IRHandler, dict(config=config)),
            (r"/api/v1/sensors", SensorsHandler, dict(config=config, sensors=sensors)),
            #(r"/api/v1/switchbot", SwitchBotHandler, dict())
        ], default_handler_class=DefaultHandler)

        # Enable no_keep_alive (Causes of 'Too many open files' Problem)
        server = tornado.httpserver.HTTPServer(web)
        server.listen(config.http_port)
        logging.info("HTTP Server started on %d", int(config.http_port))

        tornado.ioloop.IOLoop.instance().start()
    except RuntimeError as ex:
        logging.error("Initialize error: %s", str(ex))
        raise ex
