import pytest
import io
import pickle
import shelve
from xl.shelve_compat import Utf8Unpickler, ensure_shelve_compat

def test_Utf8Unpickler():
    file_object = io.BytesIO(b'')
    unpickler = Utf8Unpickler(file_object)
    assert isinstance(unpickler, Utf8Unpickler)

def test_ensure_shelve_compat():
    assert shelve.Unpickler != Utf8Unpickler
    ensure_shelve_compat()
    assert shelve.Unpickler == Utf8Unpickler
