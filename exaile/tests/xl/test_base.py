import pytest
from unittest.mock import patch, MagicMock
from mutagen import File
from xl.metadata._base import BaseFormat, CaseInsensitiveBaseFormat, NotReadable, NotWritable

test_file_path = "/check/data/music/05 - Truly.mp3"

@pytest.fixture
def base_format():
    format = BaseFormat(loc=test_file_path)
    format.mutagen = MagicMock()
    return format

@pytest.fixture
def case_insensitive_format():
    return CaseInsensitiveBaseFormat(loc=test_file_path)

def test_init_not_readable():
    with patch('xl.metadata._base.BaseFormat.load', side_effect=NotReadable):
        with pytest.raises(NotReadable):
            BaseFormat(loc=test_file_path)

def test_load(base_format):
    with patch.object(BaseFormat, 'MutagenType', MagicMock(return_value=File)):
        base_format.load()
        assert base_format.mutagen is not None

def test_save_not_writable(base_format):
    base_format.writable = False
    with pytest.raises(NotWritable):
        base_format.save()

def test_save_successful(base_format):
    base_format.writable = True
    mutagen_mock = MagicMock()
    base_format.mutagen = mutagen_mock
    base_format.save()
    mutagen_mock.save.assert_called_once()

def test_get_keys_disk(case_insensitive_format):
    case_insensitive_format.mutagen = {'Title': 'Song Title', 'artist': 'Artist Name'}
    keys = case_insensitive_format.get_keys_disk()
    assert 'title' in keys
    assert 'artist' in keys
