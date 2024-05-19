import pytest
import dbus
import os
from unittest.mock import MagicMock, patch, call
from xl.hal import UDisksPropertyWrapper, UDisksDBusWrapper, UDisksBase
from xl.providers import ProviderHandler

def test_UDisksPropertyWrapper_init():
    mock_obj = MagicMock()
    iface_type = "org.freedesktop.UDisks2.Drive"   
    wrapper = UDisksPropertyWrapper(mock_obj, iface_type)
    assert wrapper.obj == mock_obj
    assert wrapper.iface_type == iface_type

def test_UDisksPropertyWrapper_getattr():
    mock_obj = MagicMock()
    iface_type = "org.freedesktop.UDisks2.Drive"
    wrapper = UDisksPropertyWrapper(mock_obj, iface_type)
    wrapper.some_method('arg1', 'arg2')
    mock_obj.some_method.assert_called_once_with(iface_type, 'arg1', 'arg2')

def test_UDisksPropertyWrapper_repr():
    mock_obj = MagicMock()
    iface_type = "org.freedesktop.UDisks2.Drive"    
    wrapper = UDisksPropertyWrapper(mock_obj, iface_type)
    repr_string = repr(wrapper)
    expected_repr = f"<UDisksPropertyWrapper: {iface_type}>"
    assert repr_string == expected_repr

@patch('dbus.Interface')
def test_iface_property(mock_interface):
    bus = MagicMock()
    root = "some_root"
    path = "/org/freedesktop/UDisks2/drives/foo"
    iface_type = "org.freedesktop.UDisks2.Drive"
    obj = MagicMock()
    bus.get_object.return_value = obj
    wrapper = UDisksDBusWrapper(bus, root, path, iface_type)
    iface = wrapper.iface
    mock_interface.assert_called_once_with(obj, iface_type)
    assert iface is not None

@patch('dbus.Interface')
def test_props_property(mock_interface):
    bus = MagicMock()
    root = "some_root"
    path = "/org/freedesktop/UDisks2/drives/foo"
    obj = MagicMock()
    bus.get_object.return_value = obj
    wrapper = UDisksDBusWrapper(bus, root, path, "org.freedesktop.UDisks2.Drive")
    props = wrapper.props
    mock_interface.assert_called_with(obj, 'org.freedesktop.DBus.Properties')
    assert isinstance(props, UDisksPropertyWrapper)

def test_UDisksDBusWrapper_repr():
    bus = MagicMock()
    root = "some_root"
    path = "/org/freedesktop/UDisks2/drives/foo"
    iface_type = "org.freedesktop.UDisks2.Drive"
    wrapper = UDisksDBusWrapper(bus, root, path, iface_type)
    wrapper.path = path
    repr_string = repr(wrapper)
    expected_repr = f'<UDisksDBusWrapper: {iface_type} ({path})>'
    assert repr_string == expected_repr

