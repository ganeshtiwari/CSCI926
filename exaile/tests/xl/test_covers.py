import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from xl import covers
from xl.covers import Cacher, CoverManager, providers, settings, xdg
import io
import hashlib

@pytest.fixture
def cacher(tmp_path):
    return Cacher(str(tmp_path))

def test_init_directory():
    with patch('os.makedirs') as mock_makedirs:
        Cacher('test_directory')
        mock_makedirs.assert_called_once_with('test_directory')

def test_add_correctKey(cacher):
    data = b"data"
    expected_key = hashlib.sha256(data).hexdigest()
    key = cacher.add(data)
    assert key == expected_key

def test_add_correctContent(cacher):
    data = b"data"
    key = cacher.add(data)
    file_path = os.path.join(cacher.cache_dir, key)
    with open(file_path, "rb") as file:
        content = file.read()
    assert content == data

def test_hash_collision(cacher):
    data1 = b"data1"
    data2 = b"data2"
    key1 = cacher.add(data1)
    key2 = cacher.add(data2)
    assert key1 != key2 or (key1 == key2 and data1 == data2)

def test_remove_entry(cacher, tmp_path):
    test_key = "testfile"
    test_file = tmp_path / test_key
    test_file.write_text("test data")
    assert test_file.exists()
    cacher.remove(test_key)
    assert not test_file.exists()

def test_remove_usage(cacher, tmp_path):
    test_key = "testfile2"
    test_file = tmp_path / test_key
    test_file.write_text("test data")
    cacher.remove(test_key)
    assert not test_file.exists()

def test_get_entry(cacher, tmp_path):
    test_key = "testfile"
    expected_data = b"data"
    test_file = tmp_path / test_key
    test_file.write_bytes(expected_data)
    get_data = cacher.get(test_key)
    assert get_data == expected_data

def test_get_noEntry(cacher):
    non_entryKey = "missing file"
    result = cacher.get(non_entryKey)
    assert result is None

@pytest.fixture
def cover_manager():
    with patch('xl.covers.CoverManager.__init__', return_value=None):
        manager = CoverManager()
        manager.tag_fetcher = MagicMock()
        manager.localfile_fetcher = MagicMock()
        return manager

def test_tag_registration(cover_manager):
    with patch('xl.covers.settings.get_option', return_value=True) as mock_get_option, \
         patch('xl.covers.providers.register') as mock_register, \
         patch('xl.covers.providers.unregister') as mock_unregister:
        cover_manager._on_option_set(None, None, "covers/use_tags")
        mock_get_option.assert_called_once_with("covers/use_tags")
        mock_register.assert_called_once_with('covers', cover_manager.tag_fetcher)
        mock_unregister.assert_not_called()

def test_tag_unregistration(cover_manager):
    with patch('xl.covers.settings.get_option', return_value=False) as mock_get_option, \
         patch('xl.covers.providers.register') as mock_register, \
         patch('xl.covers.providers.unregister') as mock_unregister:
        cover_manager._on_option_set(None, None, "covers/use_tags")
        mock_get_option.assert_called_once_with("covers/use_tags")
        mock_unregister.assert_called_once_with('covers', cover_manager.tag_fetcher)
        mock_register.assert_not_called()

def test_localfile_registration(cover_manager):
    with patch('xl.covers.settings.get_option', return_value=True) as mock_get_option, \
         patch('xl.covers.providers.register') as mock_register, \
         patch('xl.covers.providers.unregister') as mock_unregister:
        cover_manager._on_option_set(None, None, "covers/use_localfile")
        mock_get_option.assert_called_once_with("covers/use_localfile")
        mock_register.assert_called_once_with('covers', cover_manager.localfile_fetcher)
        mock_unregister.assert_not_called()

def test_localfile_unregistration(cover_manager):
    with patch('xl.covers.settings.get_option', return_value=False) as mock_get_option, \
         patch('xl.covers.providers.register') as mock_register, \
         patch('xl.covers.providers.unregister') as mock_unregister:
        cover_manager._on_option_set(None, None, "covers/use_localfile")
        mock_get_option.assert_called_once_with("covers/use_localfile")
        mock_unregister.assert_called_once_with('covers', cover_manager.localfile_fetcher)
        mock_register.assert_not_called()

@pytest.fixture
def cover_manager():
    cm = CoverManager(location="location")
    return cm

def test_noMethods(cover_manager):
    cover_manager.methods = {}
    cover_manager.order = []
    assert cover_manager._get_methods() == []

def test_nonfixedMethods(cover_manager):
    method1 = MagicMock(fixed=False)
    method2 = MagicMock(fixed=False)
    cover_manager.methods = {'method1': method1, 'method2': method2}
    cover_manager.order = ['method1', 'method2']
    methods = cover_manager._get_methods()
    assert methods == [method1, method2]

def test_fixed_nonfixedMethods(cover_manager):
    method1 = MagicMock(fixed=True, fixed_priority=70)
    method2 = MagicMock(fixed=False)
    method3 = MagicMock(fixed=True, fixed_priority=30)
    cover_manager.methods = {'method1': method1, 'method2': method2, 'method3': method3}
    cover_manager.order = ['method1', 'method2', 'method3']
    methods = cover_manager._get_methods(fixed=True)
    assert methods == [method3, method2, method1]

def test_fixed_methodsPriority(cover_manager):
    method1 = MagicMock(fixed=True, fixed_priority=90)
    method2 = MagicMock(fixed=True, fixed_priority=50)
    method3 = MagicMock(fixed=True, fixed_priority=10)
    cover_manager.methods = {'method1': method1, 'method2': method2, 'method3': method3}
    cover_manager.order = ['method1', 'method2', 'method3']
    methods = cover_manager._get_methods(fixed=True)
    assert methods == [method3, method2, method1]

@pytest.fixture
def track():
    return MagicMock()

def test_musicbrainz_albumid(track):
    track.get_tag_raw.return_value = ['id']
    assert CoverManager._get_track_key(track) == 'musicbrainz_albumid\0id'

def test_album_albumartist(track):
    def side_effect(tag):
        if tag == 'album':
            return ['Best Album']
        elif tag == 'albumartist':
            return ['Best Artist']
        return None
    track.get_tag_raw.side_effect = side_effect    
    expected_key = 'album\0Best Album\0albumartist\0Best Artist'
    assert CoverManager._get_track_key(track) == expected_key

def test_missing_album(track):
    track.get_tag_raw.return_value = None
    assert CoverManager._get_track_key(track) is None

@pytest.fixture
def cover_manager():
    cm = CoverManager(location="location")
    cm.db = {
        'valid_key': 'cover_data_string'
    }
    return cm

def test_get_db_string_validKey(cover_manager):
    cover_manager._get_track_key = MagicMock(return_value='valid_key')    
    result = cover_manager.get_db_string(MagicMock())
    assert result == 'cover_data_string'

def test_get_db_string_invalidKey(cover_manager):
    cover_manager._get_track_key = MagicMock(return_value='invalid_key')   
    result = cover_manager.get_db_string(MagicMock())
    assert result is None

def test_get_db_string_noneKey(cover_manager):
    cover_manager._get_track_key = MagicMock(return_value=None)    
    result = cover_manager.get_db_string(MagicMock())
    assert result is None
