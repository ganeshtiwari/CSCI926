import unittest
from unittest.mock import MagicMock, patch
import pytest
from xl.trax.track import _MetadataCacher, Track

def test_metadata_cacher_init():

    timeout = 10
    maxentries = 20

    metadata_cacher = _MetadataCacher(timeout, maxentries)

    assert metadata_cacher._cache == {}
    assert metadata_cacher.timeout == timeout
    assert metadata_cacher.maxentries == maxentries
    assert metadata_cacher._cleanup_id is None

def test_metadata_cacher_entry_init():
    value = "example_value"
    time = 123.45

    entry = _MetadataCacher.Entry(value, time)
    assert entry.value == value
    assert entry.time == time

def test_metadata_cacher_entry_lt():
    entry1 = _MetadataCacher.Entry("value1", 10)
    entry2 = _MetadataCacher.Entry("value2", 20)

    assert entry1 < entry2

def test_metadata_cacher_add():

    metadata_cacher = _MetadataCacher()
    key = "example_key"
    value = "example_value"
    metadata_cacher.add(key, value)

    assert key in metadata_cacher._cache
    assert metadata_cacher._cache[key].value == value

def test_metadata_cacher_get():
    metadata_cacher = _MetadataCacher()
    key = "example_key"
    value = "example_value"
    metadata_cacher._cache[key] = _MetadataCacher.Entry(value, 0)

    result = metadata_cacher.get(key)

    assert result == value
  
@pytest.fixture
def metadata_cacher():
    return _MetadataCacher()

def test_cleanup_with_no_cleanup_id(metadata_cacher):
    metadata_cacher._cleanup_id = None

    result = metadata_cacher._MetadataCacher__cleanup()

    assert result is False

def test_cleanup_with_cleanup_id(metadata_cacher):
    metadata_cacher._cleanup_id = 123

    result = metadata_cacher._MetadataCacher__cleanup()

    assert result is False
   
def test_cleanup_with_entries(metadata_cacher):
    metadata_cacher._cache = {'key1': metadata_cacher.Entry('value1', 0)}

    result = metadata_cacher._MetadataCacher__cleanup()

    assert result is False
    assert metadata_cacher._cleanup_id is None
    

def test_add_existing_key(metadata_cacher):
    metadata_cacher._cache = {'existing_key': metadata_cacher.Entry('existing_value', 0)}
    metadata_cacher._cleanup_id = None
    metadata_cacher.maxentries = 1
    metadata_cacher.timeout = 10

    metadata_cacher.add('existing_key', 'new_value')

    assert metadata_cacher._cache['existing_key'].value == 'existing_value'
    assert metadata_cacher._cleanup_id is None

def test_add_new_key_under_max_entries(metadata_cacher):

    metadata_cacher.maxentries = 2
    metadata_cacher.timeout = 10

    metadata_cacher.add('new_key', 'new_value')

    assert metadata_cacher._cache['new_key'].value == 'new_value'
    
def test_add_new_key_over_max_entries(metadata_cacher):
    metadata_cacher.maxentries = 1
    metadata_cacher.timeout = 10
    metadata_cacher._cache = {'existing_key': metadata_cacher.Entry('existing_value', 0)}

    metadata_cacher.add('new_key', 'new_value')

    assert 'existing_key' not in metadata_cacher._cache
    assert metadata_cacher._cache['new_key'].value == 'new_value'

def test_remove_existing_key(metadata_cacher):
    metadata_cacher._cache = {'existing_key': metadata_cacher.Entry('existing_value', 0)}
    metadata_cacher.remove('existing_key')
    assert 'existing_key' not in metadata_cacher._cache

def test_remove_non_existing_key(metadata_cacher):
    metadata_cacher._cache = {'existing_key': metadata_cacher.Entry('existing_value', 0)}
    metadata_cacher.remove('non_existing_key')
    assert 'existing_key' in metadata_cacher._cache


def test_get_existing_key(metadata_cacher):
    metadata_cacher._cache = {'existing_key': metadata_cacher.Entry('existing_value', 0)}
    result = metadata_cacher.get('existing_key')
    assert result == 'existing_value'

def test_get_non_existing_key(metadata_cacher):
    metadata_cacher._cache = {'existing_key': metadata_cacher.Entry('existing_value', 0)}
    result = metadata_cacher.get('non_existing_key')
    assert result is None

@pytest.fixture
def track_instance():
  uri = "file:///path/to/track.mp3"
  return Track(uri=uri)

def test_init_with_uri(track_instance):
    assert track_instance._init is True
    assert track_instance._scan_valid is False

def test_init_without_uri():
    with pytest.raises(ValueError):
        track = Track()

def test_init_with_unpickles(track_instance):
    uri = "file:///path/to/track.mp3"
    mock_file = MagicMock(get_uri=lambda: uri)

    unpickles = {'__loc': uri, '__tag': 'value'}
    
    track_instance.__init__(_unpickles=unpickles)
    
    assert track_instance._init is True

def test_register_instance_to_global_registry():
    uri = "file:///path/to/track.mp3"
    track_instance = Track(uri=uri, scan=False) 
    
    track_instance._Track__register() 
    
    assert uri in track_instance._Track__tracksdict
    assert track_instance._Track__tracksdict[uri] == track_instance

def test_unregister_instance_from_global_registry():
    uri = "file:///path/to/track.mp3"
    track_instance = Track(uri=uri, scan=False)
    track_instance._Track__register()

    track_instance._Track__unregister()
    
    assert uri not in track_instance._Track__tracksdict

def test_set_loc():
    loc = "file:///path/to/track.mp3"
    track_instance = Track(uri=loc)
    
    track_instance.set_loc(loc, notify_changed=False)

def test_get_loc_for_io():
    loc = "file:///path/to/track.mp3"
    track_instance = Track(uri=loc)
    
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_loc_for_io() == loc

def test_get_basename():
    loc = "file:///path/to/track.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename() == expected_basename

def test_get_basename():
    loc = "file:///path/to/track.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename() == expected_basename

def test_get_basename_1():
    loc = "file:///path/to/track1.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track1.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename() == expected_basename

def test_get_basename_2():
    loc = "file:///path/to/track2.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track2.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename() == expected_basename

def test_get_basename_3():
    loc = "file:///path/to/track3.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track3.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename() == expected_basename
    
def test_get_basename_4():
    loc = "file:///path/to/track4.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track4.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename() == expected_basename

def test_get_basename_display():
    loc = "file:///path/to/track.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_get_basename_display_1():
    loc = "file:///path/to/track1.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track1.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_get_basename_display_2():
    loc = "file:///path/to/track2.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track2.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_get_basename_display_3():
    loc = "file:///path/to/track3.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track3.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_get_basename_display_4():
    loc = "file:///path/to/track4.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track4.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_get_basename_display_5():
    loc = "file:///path/to/track5.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track5.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_get_basename_display_6():
    loc = "file:///path/to/track6.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track6.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_get_basename_display_7():
    loc = "file:///path/to/track7.mp3"
    track_instance = Track(uri=loc)
    
    expected_basename = "track7.mp3"
    track_instance.set_loc(loc, notify_changed=False)
    assert track_instance.get_basename_display() == expected_basename

def test_is_local():
    uri = "file"
    track_instance = Track(uri=uri)
    
    assert track_instance.is_local() == True
  
def test_list_tags():
    uri = "File"
    track_instance = Track(uri=uri)
    
    track_instance._Track__tags = {'tag1': 'value1', 'tag2': 'value2'}
    assert track_instance.list_tags() == ['tag1', 'tag2', '__basename']

    track_instance._Track__tags = {}
    assert track_instance.list_tags() == ['__basename']

def test_list_tags_3():
    uri = "File"
    track_instance = Track(uri=uri)
    
    track_instance._Track__tags = {'tag1': 'value1', 'tag2': 'value2', 'tag3': 'value3'}
    assert track_instance.list_tags() == ['tag1', 'tag2', 'tag3', '__basename']

    track_instance._Track__tags = {}
    assert track_instance.list_tags() == ['__basename']

def test_list_tags_1():
    uri = "File"
    track_instance = Track(uri=uri)
    
    track_instance._Track__tags = {'tag1': 'value1', 'tag2': 'value2', 'tag4': 'value4'}
    assert track_instance.list_tags() == ['tag1', 'tag2', 'tag4', '__basename']

    track_instance._Track__tags = {}
    assert track_instance.list_tags() == ['__basename']

def test_list_tags_2():
    uri = "File"
    track_instance = Track(uri=uri)
    
    track_instance._Track__tags = {'tag1': 'value1', 'tag2': 'value2', 'tag5': 'value5'}
    assert track_instance.list_tags() == ['tag1', 'tag2', 'tag5', '__basename']

    track_instance._Track__tags = {}
    assert track_instance.list_tags() == ['__basename']


def test_get_tag_display():
    uri = "file"
    track_instance = Track(uri=uri)

    # Define some test data
    test_tags = {
        '__loc': '/path/to/file.mp3',
        'albumartist': 'Various Artists',
        'title': 'Sample Song',
        'tracknumber': '1',
        '__bitrate': '320000',
    }

    track_instance._Track__tags = test_tags

    display_loc = track_instance.get_tag_display('__loc', join=False)
    display_albumartist = track_instance.get_tag_display('albumartist')
    display_title = track_instance.get_tag_display('title')
    display_tracknumber = track_instance.get_tag_display('tracknumber')
    display_bitrate = track_instance.get_tag_display('__bitrate')

    assert display_loc == '/path/to/file.mp3'
    assert display_albumartist == 'Various Artists'
    assert display_title == 'Sample Song'
    assert display_tracknumber == '1'
    assert display_bitrate == '320k'
    
def test_get_tag_display_1():
    uri = "file"
    track_instance = Track(uri=uri)

    test_tags = {
        '__loc': '/path/to/file1.mp3',
        'albumartist': 'Various Artists',
        'title': 'Sample Song',
        'tracknumber': '2',
        '__bitrate': '320000',
    }

    track_instance._Track__tags = test_tags

    display_loc = track_instance.get_tag_display('__loc', join=False)
    display_albumartist = track_instance.get_tag_display('albumartist')
    display_title = track_instance.get_tag_display('title')
    display_tracknumber = track_instance.get_tag_display('tracknumber')
    display_bitrate = track_instance.get_tag_display('__bitrate')

    assert display_loc == '/path/to/file1.mp3'
    assert display_albumartist == 'Various Artists'
    assert display_title == 'Sample Song'
    assert display_tracknumber == '2'
    assert display_bitrate == '320k'
    
def test_get_tag_search():
    uri = "file"
    track_instance = Track(uri=uri)

    test_tags = {
        '__loc': '/path/to/file.mp3',
        'albumartist': 'Various Artists',
        'title': 'Sample Song',
        'tracknumber': '1',
        '__bitrate': '320000',
    }

    track_instance._Track__tags = test_tags

    search_loc = track_instance.get_tag_search('__loc', format=False)
    search_albumartist = track_instance.get_tag_search('albumartist')
    search_title = track_instance.get_tag_search('title')
    search_tracknumber = track_instance.get_tag_search('tracknumber')
    search_bitrate = track_instance.get_tag_search('__bitrate')

    assert search_loc == '/path/to/file.mp3'
    assert search_albumartist == 'albumartist=="Various Artists"'
    assert search_title == 'title=="Sample Song"'
    assert search_tracknumber == 'tracknumber=="1"'

def test_split_numerical_empty_input():
    input_value = ""
    expected_output = (None, 0)
    assert Track.split_numerical(input_value) == expected_output

def test_split_numerical_single_string():
    input_value = "10/20"
    expected_output = (10, 20)
    assert Track.split_numerical(input_value) == expected_output

def test_split_numerical_single_string_with_invalid_format():
    input_value = "abc"
    expected_output = (None, 0)
    assert Track.split_numerical(input_value) == expected_output

def test_split_numerical_list_of_strings():
    input_value = ["10/20", "30/40"]
    expected_output = [(10, 20), (30, 40)]
    assert [Track.split_numerical(val) for val in input_value] == expected_output

def test_split_numerical_list_of_strings_with_invalid_format():
    input_value = ["10/20", "abc"]
    expected_output = [(10, 20), (None, 0)]
    assert [Track.split_numerical(val) for val in input_value] == expected_output

def test_strip_leading_special_characters():
    input_value = "~!@#$%^&*()_+-={}|[]\\\";'<>?,./text"
    expected_output = "text"
    assert Track.strip_leading(input_value) == expected_output

def test_strip_leading_no_special_characters():
    input_value = "text"
    expected_output = "text"
    assert Track.strip_leading(input_value) == expected_output

def test_strip_leading_empty_input():
    input_value = ""
    expected_output = ""
    assert Track.strip_leading(input_value) == expected_output

def test_strip_leading_only_special_characters():
    input_value = "~!@#$%^&*()_+-={}|[]\\\";'<>?,./"
    expected_output = "~!@#$%^&*()_+-={}|[]\\\";'<>?,./"
    assert Track.strip_leading(input_value) == expected_output

def test_strip_leading_whitespace_characters():
    input_value = "   text"
    expected_output = "text"
    assert Track.strip_leading(input_value) == expected_output

def test_the_cutter_with_common_word():
    input_value = "the Beatles"
    expected_output = "the Beatles"
    assert Track.the_cutter(input_value) == expected_output

def test_the_cutter_without_common_word():
    input_value = "Beetles"
    expected_output = "Beetles"
    assert Track.the_cutter(input_value) == expected_output

def test_the_cutter_empty_input():
    input_value = ""
    expected_output = ""
    assert Track.the_cutter(input_value) == expected_output

def test_the_cutter_with_common_word_at_end():
    input_value = "The Beatles"
    expected_output = "The Beatles"
    assert Track.the_cutter(input_value) == expected_output

def test_the_cutter_with_common_word_case_insensitive():
    input_value = "tHe Beatles"
    expected_output = "tHe Beatles"
    assert Track.the_cutter(input_value) == expected_output
    
def test_strip_marks_with_accented_characters():
    input_value = "Café"
    expected_output = "Cafe Café"
    assert Track.strip_marks(input_value) == expected_output

def test_strip_marks_without_accented_characters():
    input_value = "Cafe"
    expected_output = "Cafe Cafe"
    assert Track.strip_marks(input_value) == expected_output

def test_strip_marks_empty_input():
    input_value = ""
    expected_output = " "
    assert Track.strip_marks(input_value) == expected_output

def test_strip_marks_with_special_characters():
    input_value = "!@#$%^&*()"
    expected_output = "!@#$%^&*() !@#$%^&*()"
    assert Track.strip_marks(input_value) == expected_output

def test_strip_marks_with_mixed_characters():
    input_value = "Café!@#$"
    expected_output = "Cafe!@#$ Café!@#$"
    assert Track.strip_marks(input_value) == expected_output
    
def test_expand_doubles_with_special_characters():
    input_value = "æ"
    expected_output = "ae"
    assert Track.expand_doubles(input_value) == expected_output

def test_expand_doubles_without_special_characters():
    input_value = "Cafe"
    expected_output = "Cafe"
    assert Track.expand_doubles(input_value) == expected_output

def test_expand_doubles_empty_input():
    input_value = ""
    expected_output = ""
    assert Track.expand_doubles(input_value) == expected_output

def test_expand_doubles_with_mixed_characters():
    input_value = "æCafé"
    expected_output = "aeCafé"
    assert Track.expand_doubles(input_value) == expected_output

def test_expand_doubles_with_lowercase_characters():
    input_value = "æcafé"
    expected_output = "aecafé"
    assert Track.expand_doubles(input_value) == expected_output

def test_lower_with_lowercase_value():
    input_value = "test"
    expected_output = "test test"
    assert Track.lower(input_value) == expected_output

def test_lower_with_uppercase_value():
    input_value = "TEST"
    expected_output = "test TEST"
    assert Track.lower(input_value) == expected_output

def test_lower_with_mixedcase_value():
    input_value = "TeSt"
    expected_output = "test TeSt"
    assert Track.lower(input_value) == expected_output

def test_lower_with_empty_input():
    input_value = ""
    expected_output = " "
    assert Track.lower(input_value) == expected_output

def test_lower_with_whitespace():
    input_value = "  test  "
    expected_output = "  test     test  "
    assert Track.lower(input_value) == expected_output

def test_quoter_with_string_value():
    input_value = 'test"quote'
    expected_output = 'test\\"quote'
    assert Track.quoter(input_value) == expected_output

def test_quoter_with_non_string_value():
    input_value = 123
    assert Track.quoter(input_value) == 123

def test_quoter_with_empty_string():
    input_value = ''
    assert Track.quoter(input_value) == ''

def test_quoter_with_whitespace():
    input_value = '  test  '
    expected_output = '  test  '
    assert Track.quoter(input_value) == expected_output

def test__get_track_count_with_empty_track_dict():
    assert Track._get_track_count() == 0

def test__get_track_count_with_non_empty_track_dict():
    uri = "file"
    Track._Track__tracksdict = {f'track_{i}': Track(uri=uri) for i in range(5)}
    assert Track._get_track_count() == 5

def test__write_rating_to_disk_with_write_to_audio_file_metadata_enabled():
    uri = "file"
    track = Track(uri=uri)
    assert track._write_rating_to_disk() is False

def test__write_rating_to_disk_with_write_to_audio_file_metadata_disabled():
    uri = "file"
    track = Track(uri=uri)
    assert track._write_rating_to_disk() is False

def test__write_rating_to_disk_with_no_format_object():
    uri = "file"
    track = Track(uri=uri)
    assert track._write_rating_to_disk() is False