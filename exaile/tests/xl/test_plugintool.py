import pytest
from tools.plugin_tool import _find_bad_plugin_versions, check, fixversion

@pytest.fixture
def new_plugins_dir(tmpdir):
    plugins_dir = tmpdir.mkdir('plugins')
    plugin1_dir = plugins_dir.mkdir('plugin1')
    plugin2_dir = plugins_dir.mkdir('plugin2')

    with open(plugin1_dir.join('PLUGININFO'), 'w') as f:
        f.write("Version='1.0'\n")
    with open(plugin2_dir.join('PLUGININFO'), 'w') as f:
        f.write("Version='2.0'\n")
    return plugins_dir

def test_find_bad_plugin_versions(new_plugins_dir):
    v = "1.0"
    result = list(_find_bad_plugin_versions(str(new_plugins_dir), v))
    assert ('plugin2', str(new_plugins_dir.join('plugin2', 'PLUGININFO')), '2.0', []) in result

def test_check():
    plugins = [('plugin1', '', '1.0', []), ('plugin2', '', '2.0', [])]
    assert check('1.0', plugins) == 1

def test_fixversion(new_plugins_dir):
    plugins = [('plugin1', str(new_plugins_dir.join('plugin1', 'PLUGININFO')), '1.0', [])]
    fixversion('2.0', plugins)
    with open(str(new_plugins_dir.join('plugin1', 'PLUGININFO'))) as f:
        contents = f.read()
        assert "Version='2.0'" in contents

