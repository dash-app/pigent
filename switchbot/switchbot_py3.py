import argparse
import struct
import sys
import time

import bluetooth
from bluetooth.ble import DiscoveryService, GATTRequester

class Scanner(object):
    service_uuid = '1bc5d5a5-0200b89f-e6114d22-000da2cb'

    def __init__(self, bt_interface=None, timeout_secs=None):
        self.bt_interface = bt_interface
        self.timeout_secs = timeout_secs if timeout_secs else 2


    def scan(self):
        service = DiscoveryService(self.bt_interface) \
            if self.bt_interface else DiscoveryService()

        devices = service.discover(self.timeout_secs)
        return list(devices.keys())


class Driver(object):
    handle = 0x16
    commands = {
        'press' : '\x57\x01\x00',
        'on'    : '\x57\x01\x01',
        'off'   : '\x57\x01\x02',
    }

    def __init__(self, device, bt_interface=None, timeout_secs=None):
        self.device = device
        self.bt_interface = bt_interface
        self.timeout_secs = timeout_secs if timeout_secs else 5
        self.req = None


    def connect(self):
        if self.bt_interface:
            self.req = GATTRequester(self.device, False, self.bt_interface)
        else:
            self.req = GATTRequester(self.device, False)

        self.req.connect(True, 'random')
        connect_start_time = time.time()
        while not self.req.is_connected():
            if time.time() - connect_start_time >= self.timeout_secs:
                raise RuntimeError('Connection to {} timed out after {} seconds'
                                   .format(self.device, self.timeout_secs))

    def run_command(self, command):
        return self.req.write_by_handle(self.handle, self.commands[command])
