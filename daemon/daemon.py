import time
from threading import Thread

from daemon.config import Config
from daemon.devices import ThermaltakeFanDevice, ThermaltakeRGBDevice
from daemon.devices.factory import device_factory
from daemon.fan_manager import FanManager, fan_controller_factory
from daemon.lighting_manager import LightingManager, lighting_controller_factory
from driver.driver import ThermaltakeRiingPlusDriver


class ThermaltakeDaemon:
    def __init__(self, initial_attached_devices: dict=None):
        self.config = Config()
        fan_controller = fan_controller_factory(**self.config.fan_controller)
        lighting_controller = lighting_controller_factory(**self.config.lighting_controller)
        self.driver = ThermaltakeRiingPlusDriver()
        self._thread = Thread(target=self._main_loop)
        self.attached_devices = {}
        self._continue = False
        self.lighting_manager = LightingManager(lighting_controller)
        self.fan_manager = FanManager(fan_controller)
        if initial_attached_devices is not None:
            for id, _type in initial_attached_devices.items():
                self.register_attached_device(id, _type)

    def register_attached_device(self, id: int, _type: str):
        dev = device_factory(self.driver, int(id), _type)
        if isinstance(dev, ThermaltakeFanDevice):
            self.fan_manager.attach_device(dev)
        if isinstance(dev, ThermaltakeRGBDevice):
            self.lighting_manager.attach_device(dev)
        self.attached_devices[id] = device_factory(self.driver, int(id), _type)

    def run(self):
        self._continue = True
        self._thread.start()
        self.lighting_manager.start()
        self.fan_manager.start()

    def stop(self):
        self._continue = False
        self.lighting_manager.stop()
        self.fan_manager.stop()
        self._thread.join()

    def _main_loop(self):
        while self._continue:
            time.sleep(1)
