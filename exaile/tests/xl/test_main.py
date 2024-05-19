import pytest
import os
import locale
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GIRepository', '2.0')
from gi.repository import GLib, Gio, Gtk, Gdk
from unittest.mock import patch, MagicMock
from xl.main import Exaile, create_argument_parser, _do_heavy_imports, exaile


@pytest.fixture(autouse=True)
def mock_imports(monkeypatch):
    mock_Gio = MagicMock()
    mock_Gtk = MagicMock()
    mock_Gdk = MagicMock()
    monkeypatch.setattr('gi.repository.Gio', mock_Gio)
    monkeypatch.setattr('gi.repository.Gtk', mock_Gtk)
    monkeypatch.setattr('gi.repository.Gdk', mock_Gdk)


def test_create_argument_parser():
    parser = create_argument_parser()
    args = parser.parse_args(['--version'])
    assert args.ShowVersion is True

def test_do_heavy_imports():
    with patch('gi.require_version') as mock_require_version:
        _do_heavy_imports()
        mock_require_version.assert_any_call('Gdk', '3.0')
        mock_require_version.assert_any_call('Gtk', '3.0')

def test_exaile_init():
    exaile_instance = Exaile()
    assert exaile_instance.quitting is False
    assert exaile_instance.loading is True

def test_exaile_version():
    with patch('xl.main.__version__', '1.0.0'), patch('sys.exit') as mock_exit:
        exaile_instance = Exaile()
        exaile_instance.options.ShowVersion = True
        exaile_instance.version()
        mock_exit.assert_called_once_with(0)

def test_set_locale():
    exaile_instance = Exaile()
    with patch('locale.getlocale', return_value=('en_US', 'UTF-8')) as mock_getlocale:
        exaile_instance._set_locale('en_US')
        mock_getlocale.assert_called_once()

def test_mainloop_init():
    exaile_instance = Exaile()
    with patch('gi.repository.GObject') as mock_GObject:
        mock_GObject.pygobject_version = (3, 10, 2)
        exaile_instance.mainloop_init()
        assert mock_GObject.pygobject_version >= (3, 10, 2)

def test_get_version():
    exaile_instance = Exaile()
    with patch('xl.main.__version__', '1.0.0'):
        assert exaile_instance.get_version() == '1.0.0'

def test_exaile():
    with patch('xl.main.Exaile._exaile', None):
        with pytest.raises(AttributeError):
            exaile()

def test_exaile_notNone():
    with patch('xl.main.Exaile._exaile', MagicMock()):
        assert exaile() is not None
