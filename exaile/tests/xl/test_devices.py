import pytest
import os
from xl.devices import Device, TransferNotSupportedError, KeyedDevice

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

class MockDevice(KeyedDevice):
    pass

def test_caching():
    device1 = MockDevice('device1')
    device2 = MockDevice('device1')
    assert device1 is device2

def test_initialization():
    key = 'key'
    device1 = MockDevice(key)
    device2 = MockDevice(key)
    assert getattr(device1, '_KeyedDevice__initialized') == True
    assert getattr(device2, '_KeyedDevice__initialized') == True

def test_destroy():
    device = MockDevice('destroy')
    MockDevice.destroy(device)
    new_device = MockDevice('destroy')
    assert new_device is not device
