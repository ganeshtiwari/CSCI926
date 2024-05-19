import pytest
import os
from xl.devices import Device, TransferNotSupportedError, KeyedDevice, DeviceManager

class Device(Device):
    def connect(self):
        if not self._connected:
            self.connected = True
    def disconnect(self):
        if self._connected:
            self.connected = False
    def transfer(self):
        pass

def test_connect():
    device = Device("device")
    assert not device.is_connected()   
    device.connect()
    assert device.is_connected()
    device.disconnect()
    assert not device.is_connected()

def test_autoconnect():
    device = Device("device")
    Device.class_autoconnect = True    
    device.autoconnect()
    assert device.is_connected()
    Device.class_autoconnect = False

def test_get_collection():
    device = Device("device")
    collection = device.get_collection()
    assert collection.name == "device"

def test_get_playlists():
    device = Device("device")
    playlists = device.get_playlists()
    assert isinstance(playlists, list)
    assert len(playlists) == 0

def test_add_tracks_nosupport():
    device = Device("device")
    with pytest.raises(TransferNotSupportedError):
        device.add_tracks(["track1", "track2"])

def test_add_tracks_support():
    class Transfer:
        def __init__(self):
            self.queue = []
        def enqueue(self, tracks):
            self.queue.extend(tracks)
        def transfer(self):
            pass
    device = Device("device")
    device.transfer = Transfer()
    device.add_tracks(["track1", "track2"])
    assert device.transfer.queue == ["track1", "track2"]   
    device.start_transfer()

@pytest.fixture
def reset_keyed_device_class():
    yield
    setattr(KeyedDevice, '__devices', {})

def test_singleton_behavior(reset_keyed_device_class):
    device1 = KeyedDevice('key1', 'Device1')
    device2 = KeyedDevice('key1', 'Device1')
    assert device1 is device2

def test_init_check(reset_keyed_device_class):
    device1 = KeyedDevice('key1', 'Device1')
    device2 = KeyedDevice('key1', 'Device1')

def test_destroy_functionality(reset_keyed_device_class):
    device1 = KeyedDevice('key1', 'Device1')
    KeyedDevice.destroy(device1)
    assert 'key1' not in getattr(KeyedDevice, '__devices')

def test_multiple_keys(reset_keyed_device_class):
    device1 = KeyedDevice('key1', 'Device1')
    device2 = KeyedDevice('key2', 'Device2')
    assert device1 is not device2
    assert device1.name != device2.name

class MockDevice:
    def __init__(self, name, connected=False):
        self.name = name
        self.connected = connected

    def get_name(self):
        return self.name

    def disconnect(self):
        self.connected = False

class MockEventLogger:
    def __init__(self):
        self.logged_events = []

    def log_event(self, event_type, manager, device):
        self.logged_events.append((event_type, manager, device.get_name()))

@pytest.fixture
def device_manager():
    return DeviceManager()

@pytest.fixture
def event_logger(monkeypatch):
    logger = MockEventLogger()
    monkeypatch.setattr('xl.devices.event.log_event', logger.log_event)
    return logger

def test_add_device_new(device_manager, event_logger):
    device = MockDevice("Device1")
    device_manager.add_device(device)
    assert device_manager.devices[device.get_name()] == device
    assert ("device_added", device_manager, "Device1") in event_logger.logged_events

def test_add_device_existing(device_manager, event_logger):
    device1 = MockDevice("Device1")
    device2 = MockDevice("Device1")
    device_manager.add_device(device1)
    device_manager.add_device(device2)
    assert device_manager.devices["Device1"] == device1
    assert device_manager.devices["Device1 (2)"] == device2
    assert ("device_added", device_manager, "Device1") in event_logger.logged_events
    assert ("device_added", device_manager, "Device1 (2)") in event_logger.logged_events

def test_add_device_multiple(device_manager, event_logger):
    device1 = MockDevice("Device1")
    device2 = MockDevice("Device1")
    device3 = MockDevice("Device1")
    device_manager.add_device(device1)
    device_manager.add_device(device2)
    device_manager.add_device(device3)
    assert device_manager.devices["Device1"] == device1
    assert device_manager.devices["Device1 (2)"] == device2
    assert device_manager.devices["Device1 (3)"] == device3
    assert ("device_added", device_manager, "Device1") in event_logger.logged_events
    assert ("device_added", device_manager, "Device1 (2)") in event_logger.logged_events
    assert ("device_added", device_manager, "Device1 (3)") in event_logger.logged_events

def test_remove_device_connected(device_manager, event_logger):
    device = MockDevice("Device1", connected=True)
    device_manager.devices[device.get_name()] = device
    device_manager.remove_device(device)
    assert device.get_name() not in device_manager.devices
    assert not device.connected
    assert ("device_removed", device_manager, "Device1") in event_logger.logged_events

def test_remove_device_disconnected(device_manager, event_logger):
    device = MockDevice("Device1")
    device_manager.devices[device.get_name()] = device
    device_manager.remove_device(device)
    assert device.get_name() not in device_manager.devices
    assert ("device_removed", device_manager, "Device1") in event_logger.logged_events

def test_remove_device_nonexistant(device_manager, event_logger):
    device = MockDevice("Device1")
    device_manager.remove_device(device)
    assert ("device_removed", device_manager, "Device1") in event_logger.logged_events

def test_get_devices_empty(device_manager):
    devices = list(device_manager.get_devices())
    assert len(devices) == 0

def test_get_devices_singleDevice(device_manager):
    device = MockDevice("Device1")
    device_manager.devices[device.get_name()] = device
    devices = list(device_manager.get_devices())
    assert len(devices) == 1
    assert devices[0] == device

def test_get_devices_multipleDevices(device_manager):
    device1 = MockDevice("Device1")
    device2 = MockDevice("Device2")
    device_manager.devices[device1.get_name()] = device1
    device_manager.devices[device2.get_name()] = device2
    devices = list(device_manager.get_devices())
    assert len(devices) == 2
    assert set(devices) == {device1, device2}

