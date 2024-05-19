import pytest
import os
import tempfile
import shelve
from io import BytesIO
from xl import event, xdg
from xl.settings import SettingsManager

def test_SettingsManager_init():
    manager = SettingsManager()
    assert isinstance(manager, SettingsManager)

def test_SettingsManager_save(tmp_path):
    location = os.path.join(tmp_path, "settings.ini")
    manager = SettingsManager(location)   
    manager.set_option("section/key", "value")
    manager.save()
    assert os.path.exists(location)

def test_SettingsManager_set_get_option():
    manager = SettingsManager()
    manager.set_option("section/key", "value")
    assert manager.get_option("section/key") == "value"

def test_SettingsManager_has_option():
    manager = SettingsManager()
    manager.set_option("section/key", "value")
    assert manager.has_option("section/key") == True

def test_SettingsManager_remove_option():
    manager = SettingsManager()
    manager.set_option("section/key", "value")
    manager.remove_option("section/key")
    assert manager.has_option("section/key") == False

def test__val_to_str():
    manager = SettingsManager()
    assert manager._val_to_str(True) == "B: True"
    assert manager._val_to_str(123) == "I: 123"
    assert manager._val_to_str(3.14) == "F: 3.14"
    assert manager._val_to_str([1, 2, 3]) == "L: [1, 2, 3]"
    assert manager._val_to_str({"a": 1, "b": 2}) == "D: {'a': 1, 'b': 2}"
    assert manager._val_to_str("testing") == "S: testing"

def test__str_to_val():
    manager = SettingsManager()
    assert manager._str_to_val("B: True") == True
    assert manager._str_to_val("I: 123") == 123
    assert manager._str_to_val("F: 3.14") == 3.14
    assert manager._str_to_val("L: [1, 2, 3]") == [1, 2, 3]
    assert manager._str_to_val("D: {'a': 1, 'b': 2}") == {"a": 1, "b": 2}
    assert manager._str_to_val("S: testing") == "testing"

def test_delayed_save():
    manager = SettingsManager()
    manager.delayed_save()
