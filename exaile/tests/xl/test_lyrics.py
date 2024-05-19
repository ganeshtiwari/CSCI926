import pytest
import os
from unittest.mock import MagicMock, patch
from xl.lyrics import LyricsCache, LyricsNotFoundException, common, event


@pytest.fixture
def lyrics_cache(tmp_path, request):
    default_value = getattr(request, 'param', 'No lyrics found')
    location = str(tmp_path / "lyrics.db")
    with patch('xl.lyrics.common.open_shelf', return_value=MagicMock()) as mock_shelf:
        mock_db = mock_shelf.return_value
        mock_db.store = {}
        mock_db.__getitem__.side_effect = lambda k: mock_db.store[k]
        mock_db.__setitem__.side_effect = lambda k, v: mock_db.store.__setitem__(k, v)
        mock_db.__delitem__.side_effect = lambda k: mock_db.store.__delitem__(k)
        mock_db.get.side_effect = lambda k, default=None: mock_db.store.get(k, default)
        mock_db.__contains__.side_effect = lambda k: k in mock_db.store
        mock_db.__iter__.side_effect = lambda: iter(mock_db.store)
        mock_db.__len__.side_effect = lambda: len(mock_db.store)
        mock_db.close = MagicMock()
        cache = LyricsCache(location, default=default_value)
        cache.db = mock_db
        yield cache

def lyrics_cache_default(tmp_path, default):
    return lyrics_cache(tmp_path, default=default)


def test_getItem_nonExisting(lyrics_cache):
    result = lyrics_cache.db.get('no_key', lyrics_cache.default)
    assert result == 'No lyrics found'

def test_set_item(lyrics_cache):
    lyrics_cache.db['new_song'] = 'new_lyrics'
    assert lyrics_cache.db.store['new_song'] == 'new_lyrics'

def test_on_quit_application(lyrics_cache):
    lyrics_cache.on_quit_application()
    lyrics_cache.db.close.assert_called_once()

@pytest.mark.parametrize("key, expected_result", [
    ('key', 'lyrics'),
    ('missing_key', 'No lyrics found')
])
def test_key_retrieval(lyrics_cache, key, expected_result):
    if key == 'key':
      lyrics_cache.db.store[key] = expected_result
    else:
      lyrics_cache.default
    result = lyrics_cache.db.get(key, lyrics_cache.default)
    assert result == expected_result

def test_keys_content(lyrics_cache):
    lyrics_cache.db.keys.return_value = ['key1', 'key2', 'key3']
    keys = lyrics_cache.keys()
    assert set(keys) == {'key1', 'key2', 'key3'}

def test_keys_empty(lyrics_cache):
    lyrics_cache.db.keys.return_value = []
    keys = lyrics_cache.keys()
    assert keys == []

def test_get_key(lyrics_cache):    
    lyrics_cache.db.__getitem__.side_effect = lambda k: 'value' if k == 'key'else KeyError
    result = lyrics_cache._get('key')
    assert result == 'value'
    
@pytest.mark.parametrize('lyrics_cache', ['global_default'], indirect=True)
def test_get_exception(lyrics_cache):
    lyrics_cache.db.__getitem__.side_effect = Exception("unexpected error")
    result = lyrics_cache._get('bad_key')
    assert result == 'global_default'

def test_set_key(lyrics_cache):
    key, value = 'test_key', 'test_value'
    lyrics_cache._set(key, value)
    assert lyrics_cache.db[key] == value
    lyrics_cache.db.sync.assert_called_once()

def test_on_set(lyrics_cache):
    lyrics_cache._set('key4', 'value4')
    lyrics_cache.db.sync.assert_called_once()

def test_setitem(lyrics_cache):
    lyrics_cache._set = MagicMock()
    key = "test_key"
    value = "test_value"
    lyrics_cache[key] = value
    lyrics_cache._set.assert_called_once_with(key, value)

def test_contains_keyPresent(lyrics_cache):
    key = "key"
    lyrics_cache.db.store[key] = "value5"
    assert key in lyrics_cache

def test_contains_noKey(lyrics_cache):
    key = "no_key"
    lyrics_cache.db.store.pop(key, None)
    assert key not in lyrics_cache

def test_delitem(lyrics_cache):
    key = "test_key"
    lyrics_cache.db.store[key] = "test_value"
    del lyrics_cache[key]
    assert key not in lyrics_cache.db.store

def test_delitem_noKey(lyrics_cache):
    key = "no_key"
    lyrics_cache.db.store.pop(key, None)
    with pytest.raises(KeyError):
        del lyrics_cache[key]

def test_len_emptyDb(lyrics_cache):
    lyrics_cache.db.store.clear()
    assert len(lyrics_cache) == 0

def test_len_nonEmptyDb(lyrics_cache):
    lyrics_cache.db.store['key1'] = 'value1'
    lyrics_cache.db.store['key2'] = 'value2'
    lyrics_cache.db.store['key3'] = 'value3'
    assert len(lyrics_cache) == 3

