import pytest
import os
import builtins
from unittest.mock import patch, mock_open, MagicMock, call, PropertyMock
from mutagen import File
from xl.metadata._base import BaseFormat, CaseInsensitiveBaseFormat, NotReadable, NotWritable, INFO_TAGS, settings

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

def test_del_tag():
    base = BaseFormat(test_file_path)
    tags = {'artist': 'Artist Name', 'title': 'Song Title'}
    base._del_tag(tags, 'artist')
    assert 'artist' not in tags
    assert 'title' in tags

class TestBaseFormat:
    def test_get_raw_withMutagen(self):
        base = BaseFormat(test_file_path)
        expected_mutagen = MagicMock()
        base.mutagen = expected_mutagen        
        result = base._get_raw()        
        assert result == expected_mutagen

    def test_get_raw_withoutMutagen(self):
        base = BaseFormat(test_file_path)
        base.MutagenType = None
        base.mutagen = None        
        result = base._get_raw()       
        assert result == {}

def test_get_tag_ExistingTag():
    base = BaseFormat(test_file_path)
    raw = {'artist': 'Artist Name', 'title': 'Song Title'}
    tag = 'artist'
    result = base._get_tag(raw, tag)
    assert result == 'Artist Name'

def test_get_tag_noneExistingTag():
    base = BaseFormat(test_file_path)
    raw = {'artist': 'Artist Name', 'title': 'Song Title'}
    tag = 'album'
    result = base._get_tag(raw, tag)
    assert result is None

def test_set_tag_Value():
    base = BaseFormat(test_file_path)
    raw = {}
    tag = 'genre'
    value = 'Jazz'
    base._set_tag(raw, tag, value)
    assert raw[tag] == value

def test_set_tag_noneValue():
    base = BaseFormat(test_file_path)
    raw = {'genre': 'Jazz'}
    tag = 'genre'
    value = None
    base._set_tag(raw, tag, value)
    assert raw[tag] is None

def test_get_keys_disk_empty():
    base = BaseFormat(test_file_path)
    base._get_raw = MagicMock(return_value={})
    base._reverse_mapping = {}
    assert base.get_keys_disk() == []

def test_get_keys_disk_noReverseMapping():
    base = BaseFormat(test_file_path)
    base._get_raw = MagicMock(return_value={'artist': 'Coldplay', 'album': 'Parachutes'})
    base._reverse_mapping = {}
    assert base.get_keys_disk() == ['artist', 'album']

def test_get_keys_disk_reverseMapping():
    base = BaseFormat(test_file_path)
    base._get_raw = MagicMock(return_value={'TPE1': 'Coldplay', 'TALB': 'Parachutes'})
    base._reverse_mapping = {'TPE1': 'artist', 'TALB': 'album'}
    assert base.get_keys_disk() == ['artist', 'album']

def test_get_keys_disk_unmappedTags():
    base = BaseFormat(test_file_path)
    base._get_raw = MagicMock(return_value={'TPE1': 'Coldplay', 'XYZ': 'Data'})
    base._reverse_mapping = {'TPE1': 'artist'}
    assert base.get_keys_disk() == ['artist', 'XYZ']

def test_get_keys_disk_caseInsensitive():
    base = BaseFormat(test_file_path)
    base.case_sensitive = False
    base._get_raw = MagicMock(return_value={'tpe1': 'Coldplay', 'talb': 'Parachutes'})
    base._reverse_mapping = {'tpe1': 'artist', 'talb': 'album'}
    assert base.get_keys_disk() == ['artist', 'album']

def test_read_all_noBlacklist():
    base = BaseFormat(test_file_path)
    base.get_keys_disk = MagicMock(return_value=['artist', 'album'])
    base.ignore_tags = set()
    base._remove_internal_tag = MagicMock(return_value=False)
    base.read_tags = MagicMock(return_value={'artist': ['Coldplay'], 'album': ['Parachutes']})
    assert base.read_all() == {'artist': ['Coldplay'], 'album': ['Parachutes']}
    base.read_tags.assert_called_once_with(INFO_TAGS + ['artist', 'album'])

def test_read_all_ignoreTags():
    base = BaseFormat(test_file_path)
    base.get_keys_disk = MagicMock(return_value=['artist', 'lyrics', 'album'])
    base.ignore_tags = set(['lyrics'])
    base._remove_internal_tag = MagicMock(return_value=False)
    base.read_tags = MagicMock(return_value={'artist': ['Coldplay'], 'album': ['Parachutes']})
    assert base.read_all() == {'artist': ['Coldplay'], 'album': ['Parachutes']}
    base.read_tags.assert_called_once_with(INFO_TAGS + ['artist', 'album'])

def test_read_all_internalTags():
    base = BaseFormat(test_file_path)
    base.get_keys_disk = MagicMock(return_value=['artist', '__version', 'album'])
    base.ignore_tags = set()
    base._remove_internal_tag = MagicMock(side_effect=lambda x: x.startswith('__'))
    base.read_tags = MagicMock(return_value={'artist': ['Coldplay'], 'album': ['Parachutes']})
    assert base.read_all() == {'artist': ['Coldplay'], 'album': ['Parachutes']}
    base.read_tags.assert_called_once_with(INFO_TAGS + ['artist', 'album'])

def test_read_all_full():
    base = BaseFormat(test_file_path)
    base.get_keys_disk = MagicMock(return_value=['artist', '__version', 'lyrics', 'album'])
    base.ignore_tags = set(['lyrics'])
    base._remove_internal_tag = MagicMock(side_effect=lambda x: x.startswith('__'))
    base.read_tags = MagicMock(return_value={'artist': ['Coldplay'], 'album': ['Parachutes']})
    assert base.read_all() == {'artist': ['Coldplay'], 'album': ['Parachutes']}
    base.read_tags.assert_called_once_with(INFO_TAGS + ['artist', 'album'])

def test_read_tags_infoTags():
    base = BaseFormat(test_file_path)
    base._get_raw = MagicMock()
    base.get_info = MagicMock(side_effect=lambda x: 'info_data' if x == '__bitrate' else 'other_info')
    base.tag_mapping = {}
    tags = ['__bitrate', '__length']
    expected = {'__bitrate': ['info_data'], '__length': ['other_info']}
    assert base.read_tags(tags) == expected
    base.get_info.assert_any_call('__bitrate')
    base.get_info.assert_any_call('__length')

def test_read_tags_mappedTags():
    base = BaseFormat(test_file_path)
    raw_data = {'TPE1': 'Coldplay', 'TALB': 'Parachutes'}
    base._get_raw = MagicMock(return_value=raw_data)
    base._get_tag = MagicMock(side_effect=lambda raw, tag: raw[tag])
    base.tag_mapping = {'artist': 'TPE1', 'album': 'TALB'}
    tags = ['artist', 'album']
    expected = {'artist': ['Coldplay'], 'album': ['Parachutes']}
    assert base.read_tags(tags) == expected
    base._get_tag.assert_any_call(raw_data, 'TPE1')
    base._get_tag.assert_any_call(raw_data, 'TALB')

def test_read_tags_otherTags():
    base = BaseFormat(test_file_path)
    raw_data = {'genre': 'Rock', 'year': '2000'}
    base._get_raw = MagicMock(return_value=raw_data)
    base._get_tag = MagicMock(side_effect=lambda raw, tag: raw[tag])
    base.tag_mapping = {}
    tags = ['genre', 'year']
    expected = {'genre': ['Rock'], 'year': ['2000']}
    assert base.read_tags(tags) == expected
    base._get_tag.assert_any_call(raw_data, 'genre')
    base._get_tag.assert_any_call(raw_data, 'year')

def test_read_tags_notFound():
    base = BaseFormat(test_file_path)
    raw_data = {'artist': 'Coldplay'}
    base._get_raw = MagicMock(return_value=raw_data)
    base._get_tag = MagicMock(side_effect=lambda raw, tag: raw.get(tag, None))
    base.tag_mapping = {}
    tags = ['artist', 'album']
    expected = {'artist': ['Coldplay'], 'album': [None]}
    assert base.read_tags(tags) == expected
    base._get_tag.assert_any_call(raw_data, 'artist')
    base._get_tag.assert_any_call(raw_data, 'album')

def test_write_tags_notWritable():
    base = BaseFormat(test_file_path)
    base.MutagenType = None
    base.writable = False
    with pytest.raises(NotWritable):
        base.write_tags({'artist': ['Coldplay']})

def test_write_tags_success():
    base = BaseFormat(test_file_path)
    base.MutagenType = True
    base.writable = True
    base._get_raw = MagicMock(return_value={'tags': True})
    base._set_tag = MagicMock()
    base._del_tag = MagicMock()
    base.save = MagicMock()
    base.tag_mapping = {'artist': 'TPE1'}
    base.others = True
    tagdict = {'artist': ['Coldplay'], 'album': ['Parachutes']}
    base.write_tags(tagdict)
    calls = [call(base._get_raw.return_value, 'TPE1', ['Coldplay']),
             call(base._get_raw.return_value, 'album', ['Parachutes'])]       
    base._set_tag.assert_has_calls(calls, any_order=True)
    base.save.assert_called_once()

def test_write_tags_delete():
    base = BaseFormat(test_file_path)
    base.MutagenType = True
    base.writable = True
    base._get_raw = MagicMock(return_value={'tags': True})
    base._set_tag = MagicMock()
    base._del_tag = MagicMock()
    base.save = MagicMock()
    base.tag_mapping = {'artist': 'TPE1'}
    base.others = True
    tagdict = {'artist': None}
    base.write_tags(tagdict)
    base._del_tag.assert_called_once_with(base._get_raw.return_value, 'TPE1')
    base.save.assert_called_once()

def test_write_tags_internal():
    base = BaseFormat(test_file_path)
    base.MutagenType = True
    base.writable = True
    base._get_raw = MagicMock(return_value={'tags': True})
    base._set_tag = MagicMock()
    base._del_tag = MagicMock()
    base.save = MagicMock()
    base._remove_internal_tag = MagicMock(side_effect=lambda x: x.startswith('__'))
    base.tag_mapping = {}
    base.others = True
    tagdict = {'__internal': ['data'], 'genre': ['Rock']}
    base.write_tags(tagdict)
    base._set_tag.assert_called_once_with(base._get_raw.return_value, 'genre', ['Rock'])
    base._del_tag.assert_not_called()
    base.save.assert_called_once()

def test_get_info_length():
    base = BaseFormat(test_file_path)
    base.get_length = MagicMock(return_value=360)
    assert base.get_info("__length") == 360
    base.get_length.assert_called_once()

def test_get_info_bitrate():
    base = BaseFormat(test_file_path)
    base.get_bitrate = MagicMock(return_value=192000)
    assert base.get_info("__bitrate") == 192000
    base.get_bitrate.assert_called_once()

def test_get_info_invalid():
    base = BaseFormat(test_file_path)
    with pytest.raises(KeyError):
        base.get_info("invalid_info")

def test_get_length_noData(base_format):
    base = BaseFormat(test_file_path)
    base.mutagen = MagicMock(info=MagicMock(spec=[]))
    base._get_raw = MagicMock(side_effect=KeyError)    
    assert base.get_length() is None

def test_get_length_mutagen_raw(base_format):
    base = BaseFormat(test_file_path)
    base.mutagen = MagicMock(info=MagicMock(spec=[]))
    base._get_raw = MagicMock(return_value={'__length': 300})
    assert base.get_length() == 300

def test_get_length_mutagen(base_format):
    type(base_format).mutagen = PropertyMock()
    type(base_format.mutagen).info = PropertyMock(return_value=MagicMock(length=320))    
    assert base_format.get_length() == 320

def test_get_bitrate_mutagen(base_format):
    type(base_format.mutagen.info).bitrate = PropertyMock(return_value=256000)
    assert base_format.get_bitrate() == 256000

def test_stars_to_rating_int():
    base = BaseFormat(test_file_path)
    result = base._stars_to_rating(5)
    assert result == 5

def test_stars_to_rating_float():
    base = BaseFormat(test_file_path)
    result = base._stars_to_rating(4.0)
    assert result == 4

def test_stars_to_rating_string():
    base = BaseFormat(test_file_path)
    result = base._stars_to_rating("3")
    assert result == 3

def test_stars_to_rating_invalidInput():
    base = BaseFormat(test_file_path)
    with pytest.raises(ValueError):
      base._stars_to_rating("abc")

def test_rating_to_stars_zeroBelowRange():
    base = BaseFormat(test_file_path)
    assert base._rating_to_stars(0) == 0
    assert base._rating_to_stars(-1) == 0
    assert base._rating_to_stars(-20) == 0

def test_rating_to_stars_lowRange():
    base = BaseFormat(test_file_path)
    assert base._rating_to_stars(1) == 20
    assert base._rating_to_stars(15) == 20
    assert base._rating_to_stars(29) == 20

def test_rating_to_stars_mediumLowRange():
    base = BaseFormat(test_file_path)
    assert base._rating_to_stars(30) == 40
    assert base._rating_to_stars(40) == 40
    assert base._rating_to_stars(49) == 40

def test_rating_to_stars_mediumRange():
    base = BaseFormat(test_file_path)
    assert base._rating_to_stars(50) == 60
    assert base._rating_to_stars(60) == 60
    assert base._rating_to_stars(69) == 60

def test_rating_to_stars_highRange():
    base = BaseFormat(test_file_path)
    assert base._rating_to_stars(70) == 80
    assert base._rating_to_stars(80) == 80
    assert base._rating_to_stars(89) == 80

def test_rating_to_stars_highestRange():
    base = BaseFormat(test_file_path)
    assert base._rating_to_stars(90) == 100
    assert base._rating_to_stars(100) == 100
    assert base._rating_to_stars(150) == 100

@pytest.mark.parametrize("tag", ["__private", "__metadata", "__version"])
def test_remove_internalTags(tag):
    base = BaseFormat(test_file_path)
    assert base._remove_internal_tag(tag) is True

@patch('xl.metadata._base.settings.get_option', return_value=True)
def test_keep_ratingTag(mock_settings):
    base = BaseFormat(test_file_path)
    tag = "__rating"
    assert base._remove_internal_tag(tag) is False

@patch('xl.metadata._base.settings.get_option', return_value=False)
def test_remove_ratingTag(mock_settings):
    base = BaseFormat(test_file_path)
    tag = "__rating"
    assert base._remove_internal_tag(tag) is True

@pytest.mark.parametrize("tag", ["artist", "title", "album"])
def test_nonInternal_tags(tag):
    base = BaseFormat(test_file_path)
    assert base._remove_internal_tag(tag) is False

@pytest.fixture
def case_insensitive_base_format():
    cif = CaseInsensitiveBaseFormat(loc=test_file_path)
    cif._get_raw = MagicMock()
    return cif

def test_get_keys_disk_lowercase(case_insensitive_base_format):
    test_data = {'Artist': 'Coldplay', 'ALBUM': 'Parachutes', 'title': 'Yellow'}
    case_insensitive_base_format._get_raw.return_value = test_data
    expected_keys = ['artist', 'album', 'title']
    actual_keys = case_insensitive_base_format.get_keys_disk()
    assert actual_keys == expected_keys

def test_get_keys_disk_empty(case_insensitive_base_format):
    case_insensitive_base_format._get_raw.return_value = {}
    expected_keys = []
    actual_keys = case_insensitive_base_format.get_keys_disk()
    assert actual_keys == expected_keys

