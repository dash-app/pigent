#!/usr/bin/python3

import fcntl
import os
import struct

# LIRC userspace API ioctls (from <linux/lirc.h>).
# IR transmission is delegated to the kernel `gpio-ir-tx` driver, which exposes
# `/dev/lirc0` and performs the 38kHz carrier modulation in hardware-timed
# kernel context. Userspace only writes pulse/space durations in microseconds.
LIRC_MODE_PULSE = 0x00000002

LIRC_SET_SEND_MODE = 0x40046911
LIRC_SET_SEND_CARRIER = 0x40046913
LIRC_SET_SEND_DUTY_CYCLE = 0x40046915

LIRC_DEVICE = os.getenv("PIGENT_LIRC_DEVICE", default="/dev/lirc0")
CARRIER_HZ = 38000
DUTY_CYCLE = 50


def send(gpio: int, signal: list) -> None:
    """Send IR Signal via the kernel LIRC interface.

    `gpio` is retained for API compatibility but is configured at the kernel
    level via the `gpio-ir-tx` device-tree overlay (e.g. `dtoverlay=gpio-ir-tx,
    gpio_pin=17`). It is not used here.

    `signal` is a sequence of mark/space durations in microseconds, starting
    with a mark and alternating thereafter, matching the existing pigpio
    signal format.
    """

    if len(signal) == 0:
        return

    # LIRC requires the buffer to start with a pulse and end with a pulse.
    # If the caller passed a trailing space, drop it.
    if len(signal) % 2 == 0:
        signal = signal[:-1]

    try:
        fd = os.open(LIRC_DEVICE, os.O_WRONLY)
    except OSError as ex:
        raise RuntimeError(f"failed to open {LIRC_DEVICE}: {ex}") from ex

    try:
        try:
            fcntl.ioctl(fd, LIRC_SET_SEND_MODE,
                        struct.pack("I", LIRC_MODE_PULSE))
            fcntl.ioctl(fd, LIRC_SET_SEND_CARRIER,
                        struct.pack("I", CARRIER_HZ))
            fcntl.ioctl(fd, LIRC_SET_SEND_DUTY_CYCLE,
                        struct.pack("I", DUTY_CYCLE))
        except OSError as ex:
            raise RuntimeError(f"failed to configure LIRC device: {ex}") from ex

        buf = struct.pack(f"{len(signal)}I", *(int(v) for v in signal))
        try:
            os.write(fd, buf)
        except OSError as ex:
            raise RuntimeError(f"failed to transmit IR signal: {ex}") from ex
    finally:
        os.close(fd)
