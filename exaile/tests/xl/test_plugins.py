import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
import tarfile
from xl.plugins import PluginsManager, InvalidPluginError, PluginExistsError
import pkgutil
import gi
gi.require_version('GIRepository', '2.0')
from gi.repository import GIRepository


@pytest.fixture
def mock_xdg():
    with patch('xl.plugins.xdg.get_user_plugin_dir', return_value='/test/user/plugins'), \
         patch('xl.plugins.xdg.get_plugin_dirs', return_value=['/dir1', '/dir2']):
        yield

@pytest.fixture
def mock_os_path():
    with patch('xl.plugins.os.path.exists') as mock_exists:
        mock_exists.side_effect = lambda path: path in ['/dir1/myplugin']
        yield mock_exists

@pytest.fixture
def plugins_manager(mock_xdg, mock_os_path):
    return PluginsManager(exaile="ExaileInstance", load=True)

def test_plugins_manager_init(plugins_manager):
    assert plugins_manager.user_installed_plugindir == '/test/user/plugins'
    assert plugins_manager.loaded_plugins == {}
    assert plugins_manager.enabled_plugins == {}
    assert plugins_manager.exaile == "ExaileInstance"
    assert plugins_manager.load is True

def test_findplugin(plugins_manager):
    found_path = plugins_manager._PluginsManager__findplugin('myplugin')
    assert found_path == '/dir1/myplugin'

def test_findplugin_no_plugin(plugins_manager, mock_os_path):
    mock_os_path.side_effect = lambda path: False
    found_path = plugins_manager._PluginsManager__findplugin('unknownplugin')
    assert found_path is None

@pytest.fixture
def setup_plugins_manager():
    manager = PluginsManager(exaile="ExaileInstance")
    manager.user_installed_plugindir = '/test/plugins/dir'
    return manager

def test_load_plugin_loaded(setup_plugins_manager):
    setup_plugins_manager.loaded_plugins = {'test_plugin': 'loaded_plugin_instance'}
    result = setup_plugins_manager.load_plugin('test_plugin')
    assert result == 'loaded_plugin_instance'


@patch('xl.plugins.importlib.util')
@patch('xl.plugins.os.path.join')
@patch('xl.plugins.os.path.exists', return_value=True)
def test_load_plugin_new(mock_exists, mock_join, mock_importlib, setup_plugins_manager):
    spec_mock = MagicMock()
    module_mock = MagicMock()
    mock_importlib.util.spec_from_file_location.return_value = spec_mock
    mock_importlib.util.module_from_spec.return_value = module_mock
    spec_mock.loader.exec_module.return_value = None
    setup_plugins_manager.load_plugin('new_plugin')
    assert 'new_plugin' in setup_plugins_manager.loaded_plugins

@patch('xl.plugins.tarfile.open')
@patch('xl.plugins.os.path.basename')
def test_install_plugin_success(mock_basename, mock_tarfile, setup_plugins_manager):
    mock_tar = MagicMock()
    mock_tar.getmembers.return_value = [MagicMock(name='plugin_name/valid_file')]
    mock_tarfile.return_value = mock_tar
    mock_basename.return_value = 'plugin_name.tar.gz'  
    with patch('xl.plugins.PluginsManager.list_installed_plugins', return_value=[]):
        result = setup_plugins_manager.install_plugin('/test/plugin_name.tar.gz')
        assert result == 'plugin_name'

@patch('xl.plugins.tarfile.open', side_effect=tarfile.ReadError)
def test_install_plugin_invalid(mock_tarfile, setup_plugins_manager):
    with pytest.raises(InvalidPluginError):
        setup_plugins_manager.install_plugin('/test/plugin_name.tar.gz')

def test_enable_plugin_not_found(setup_plugins_manager):
    with patch('xl.plugins.PluginsManager.load_plugin', return_value=None):
        with pytest.raises(Exception, match="Error loading plugin"):
            setup_plugins_manager.enable_plugin('nonexistent_plugin')

def test_disable_plugin_not_found(setup_plugins_manager):
    result = setup_plugins_manager.disable_plugin('nonexistent_plugin')
    assert result is False

@patch('xl.plugins.logger')
def test_disable_plugin_error(mock_logger, setup_plugins_manager):
    setup_plugins_manager.enabled_plugins = {'test_plugin': MagicMock(disable=MagicMock(side_effect=Exception("Error disabling")))}
    with pytest.raises(Exception):
        setup_plugins_manager.disable_plugin('test_plugin')
      
def test_uninstall_plugin_notUserInstalled(setup_plugins_manager):
    with patch('xl.plugins.PluginsManager.is_user_installed', return_value=False):
        with pytest.raises(Exception, match="Cannot remove built-in plugins"):
            setup_plugins_manager.uninstall_plugin('builtin_plugin')

def test_uninstall_plugin_success(setup_plugins_manager):
    with patch('xl.plugins.PluginsManager.is_user_installed', return_value=True), \
         patch('xl.plugins.shutil.rmtree') as mock_rmtree:
        setup_plugins_manager.uninstall_plugin('user_plugin')
        mock_rmtree.assert_called_once_with('/test/plugins/dir/user_plugin')

def test_is_user_installed_true(setup_plugins_manager):
    with patch('xl.plugins.os.path.isdir', return_value=True):
        assert setup_plugins_manager.is_user_installed('test_plugin') is True

def test_is_user_installed_false(setup_plugins_manager):
    with patch('xl.plugins.os.path.isdir', return_value=False):
        assert setup_plugins_manager.is_user_installed('test_plugin') is False

def test_get_plugin_info(setup_plugins_manager):
    plugin_info_path = '/test/path/PLUGININFO'
    test_data = 'key1="value1"\nkey2="value2"\n'
    with patch('xl.plugins.os.path.join', return_value=plugin_info_path), \
         patch('builtins.open', mock_open(read_data=test_data)):
        info = setup_plugins_manager.get_plugin_info('plugin_name')
        assert info['key1'] == 'value1'
        assert info['key2'] == 'value2'


def test_is_compatible_true(setup_plugins_manager):
    info = {'Platforms': ['linux', 'win32']}
    assert setup_plugins_manager.is_compatible(info) is True

def test_is_compatible_false(setup_plugins_manager):
    info = {'Platforms': ['darwin']}
    assert setup_plugins_manager.is_compatible(info) is False

def test_is_potentially_broken(setup_plugins_manager):
    with patch('pkgutil.find_loader', return_value=None), \
         patch('gi.repository.GIRepository.Repository.get_default'):
        info = {'RequiredModules': ['gtk', 'gi:Gtk']}
        assert setup_plugins_manager.is_potentially_broken(info) is True

def test_teardown(setup_plugins_manager):
    mock_plugin = MagicMock()
    setup_plugins_manager.enabled_plugins = {'plugin_name': mock_plugin}
    with patch('xl.plugins.logger'):
        setup_plugins_manager.teardown('main')
        mock_plugin.teardown.assert_called_once_with('main')

def test_save_enabled_load_true(plugins_manager):
    plugins_manager.enabled_plugins = {'plugin1': MagicMock(), 'plugin2': MagicMock()}
    with patch('xl.plugins.settings.set_option') as mock_set_option:
        plugins_manager.save_enabled()
        mock_set_option.assert_called_once_with("plugins/enabled", list(plugins_manager.enabled_plugins.keys()))

def test_save_enabled_load_false(plugins_manager):
    plugins_manager.load = False
    with patch('xl.plugins.settings.set_option') as mock_set_option:
        plugins_manager.save_enabled()
        mock_set_option.assert_not_called()

def test_load_enabled_plugins(plugins_manager):
    with patch('xl.plugins.settings.get_option', return_value=['plugin1', 'plugin2']), \
         patch('xl.plugins.PluginsManager.enable_plugin') as mock_enable_plugin:
        plugins_manager.load_enabled()
        assert mock_enable_plugin.call_count == 2
        mock_enable_plugin.assert_any_call('plugin1')
        mock_enable_plugin.assert_any_call('plugin2')

def test_load_enabled_exception(plugins_manager):
    with patch('xl.plugins.settings.get_option', return_value=['plugin1']), \
         patch('xl.plugins.PluginsManager.enable_plugin', side_effect=Exception):
        plugins_manager.load_enabled()
