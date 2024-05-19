import pytest
import os
import sys
from gi.repository import GLib
from unittest.mock import patch, MagicMock
from xl.version import exaile_dir
import xl.xdg
from xl.xdg import (get_config_dir, fhs_compliant, get_data_home_path, get_data_dir, get_cache_dir, get_logs_dir, data_dirs, config_dirs, 
                         get_config_dirs, get_data_dirs, get_plugin_dirs, os, _get_path, get_user_plugin_dir, _make_missing_dirs, get_plugin_data_dir, get_last_dir, get_config_path, get_data_path)

@pytest.fixture
def setup_environment(tmp_path):
    with patch('os.path.expanduser', return_value=str(tmp_path)), \
         patch('os.getenv', side_effect=lambda key, default=None: default), \
         patch('os.path.exists', return_value=True), \
         patch('xl.xdg.exaile_dir', new=str(tmp_path / 'exaile')):
        yield tmp_path

def test_get_config_dir(setup_environment):
    assert get_config_dir().endswith('exaile')

def test_get_data_dir(setup_environment):
    assert get_data_dir().endswith('exaile')

def test_get_cache_dir(setup_environment):
    assert get_cache_dir().endswith('exaile')

def test_get_logs_dir(setup_environment):
    if os.sys.platform == 'win32':
        expected_logs_dir = 'exaile/logs'
    else:
        expected_logs_dir = '.cache/exaile/logs'
    logs_dir = get_logs_dir()
    assert logs_dir.endswith(expected_logs_dir)

def test_get_data_dirs(setup_environment):
    data_dirs = get_data_dirs()
    assert len(data_dirs) > 0
    assert data_dirs[0].endswith('exaile')

def test_get_plugin_dirs(setup_environment):
    plugin_dirs = get_plugin_dirs()
    assert len(plugin_dirs) > 0
    assert 'plugins' in plugin_dirs[0]

@pytest.mark.parametrize("path_elements, expected", [
    (('settings', 'config.xml'), 'config.xml'),
    (('media', 'playlists'), 'playlists')
])
def test_get_data_home_path(setup_environment, path_elements, expected):
    result = get_data_home_path(*path_elements)
    assert expected in result, f"Path should include '{expected}'"

@pytest.fixture
def mock_environment(tmp_path):
    with patch('os.path.expanduser', return_value=str(tmp_path)), \
         patch('os.getenv', side_effect=lambda key, default=None: default), \
         patch('os.path.exists', return_value=True):
        yield tmp_path

def test_get_logs_dir_platform(mock_environment):
    with patch('sys.platform', 'win32'):
        logs_dir = get_logs_dir()
        assert logs_dir.endswith('logs')
    with patch('sys.platform', 'linux'):
        logs_dir = get_logs_dir()
        assert logs_dir.endswith('logs')

def test_plugin_dirs_existence(mock_environment):
    with patch('os.path.exists', side_effect=lambda x: 'valid' in x):
        plugin_dirs = ["/invalid/testpath", "/valid/testpath"]
        valid_dirs = [d for d in plugin_dirs if os.path.exists(d)]
        assert "/valid/testpath" in valid_dirs

@pytest.fixture(autouse=True)
def setup():
    xl.xdg._make_missing_dirs()
    yield

def test_get_plugin_data_dir():
    assert os.path.exists(get_plugin_data_dir())

def test_make_missing_dirs():
    _make_missing_dirs()

def test_get_user_plugin_dir():
    assert os.path.exists(get_user_plugin_dir())

def test_get_path_directory(tmp_path):
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    result_path = xl.xdg._get_path([str(tmp_path)], "test_dir")
    assert result_path == str(dir_path)
  
@pytest.mark.parametrize("function, basedirs", [
    (get_data_path, data_dirs),
    (get_config_path, config_dirs)
])
def test_get_path(function, basedirs):
    subpath_elements = ('tmp', 'nested', 'directory')
    expected_path = '/test/directory/tmp/nested/directory'    
    with patch('os.path.join', return_value=expected_path), \
         patch('os.path.exists', return_value=True):
        result = function(*subpath_elements)
        assert result == expected_path
    with patch('os.path.join', return_value=expected_path), \
         patch('os.path.exists', return_value=False):
        result = function(*subpath_elements)
        assert result is None

@pytest.mark.parametrize("function, basedirs", [
    (get_data_path, data_dirs),
    (get_config_path, config_dirs)
])
def test_get_path_exist_false(function, basedirs):
    subpath_elements = ('tmp', 'nested', 'directory')
    expected_path = '/test/directory/tmp/nested/directory'    
    with patch('os.path.join', return_value=expected_path), \
         patch('os.path.exists', return_value=False) as mock_exists:
        result = function(*subpath_elements, check_exists=False)
        mock_exists.assert_not_called()
        assert result == expected_path

def test_get_last_dir():
    expected_dir = '/expected/last/directory'
    with patch('xl.xdg.lastdir', new=expected_dir):
        result = get_last_dir()
        assert result == expected_dir

@pytest.mark.parametrize("function, basedirs", [
    (get_data_path, data_dirs),
    (get_config_path, config_dirs)
])
def test_get_path_valid(function, basedirs):
    subpath_elements = ('folder', 'file.txt')
    expected_path = '/expected/folder/file.txt'
    with patch('os.path.join', return_value=expected_path), \
         patch('os.path.exists', return_value=True):
        result = function(*subpath_elements)
        assert result == expected_path

@pytest.mark.parametrize("function, basedirs", [
    (get_data_path, data_dirs),
    (get_config_path, config_dirs)
])
def test_get_path_nonexistent(function, basedirs):
    subpath_elements = ('nonexistent', 'folder')
    expected_path = '/expected/nonexistent/folder'
    with patch('os.path.join', return_value=expected_path), \
         patch('os.path.exists', return_value=False):
        result = function(*subpath_elements)
        assert result is None

@pytest.mark.parametrize("function, basedirs", [
    (get_data_path, data_dirs),
    (get_config_path, config_dirs)
])
def test_get_path_ignore_existence(function, basedirs):
    subpath_elements = ('test', 'tmp')
    expected_path = '/expected/test/tmp'
    with patch('os.path.join', return_value=expected_path), \
         patch('os.path.exists', return_value=False):
        result = function(*subpath_elements, check_exists=False)
        assert result == expected_path

