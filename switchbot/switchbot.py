from . import switchbot_py3


def run(mac: str, cmd: str):
    # call swtichbot api
    try:
        driver = switchbot_py3.Driver(
            device=mac, bt_interface=None, timeout_secs=5)
        driver.connect()

        driver.run_command(cmd)
    except Exception:
        raise Exception
