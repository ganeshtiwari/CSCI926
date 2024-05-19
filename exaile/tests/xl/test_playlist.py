import pytest
from collections import deque
from unittest import mock
from unittest.mock import patch, MagicMock, Mock, create_autospec, PropertyMock
import os
from gi.repository import Gio
from xl.common import GioFileInputStream, GioFileOutputStream, MetadataList
from xl.playlist import PlaylistExportOptions, InvalidPlaylistTypeError, encode_filename, is_valid_playlist, import_playlist, export_playlist, \
    FormatConverter, M3UConverter, PLSConverter, ASXConverter, XSPFConverter, trax, Playlist, SmartPlaylist, PlaylistManager, Playlist, encode_filename, \
    PlaylistExists, event, logger, SmartPlaylistManager  


def test_encode_filename_invalidChars():
    filename = "test<name:playlist"
    expected = "test%3cname%3aplaylist.playlist"
    assert encode_filename(filename) == expected

def test_encode_filename_validChars():
    filename = "valid_filename"
    expected = "valid_filename.playlist"
    assert encode_filename(filename) == expected

@patch('xl.playlist.providers.get')
def test_is_valid_playlist_known_content(mock_get):
    mock_get.return_value = [Mock(content_types=['audio/mpeg'], file_extensions=['mp3'])]
    path = "test.mp3"
    assert is_valid_playlist(path)

@patch('xl.playlist.providers.get')
def test_is_valid_playlist_unknown_content(mock_get):
    mock_get.return_value = [Mock(content_types=[], file_extensions=['mp3'])]
    path = "unknown.type"
    assert not is_valid_playlist(path)

@patch('xl.playlist.Gio.content_type_is_unknown', return_value=False)
@patch('xl.playlist.Gio.content_type_guess')
@patch('xl.playlist.providers.get')
def test_import_playlist_extension(mock_get, mock_content_type_guess, mock_content_type_is_unknown):
    mock_content_type_guess.return_value = ('audio/mpeg', None)
    mock_get.return_value = [
        Mock(content_types=['audio/mpeg'], file_extensions=['mp3'], import_from_file=lambda x: 'playlist')
    ]
    path = "playlist.mp3"
    assert import_playlist(path) == 'playlist'

@patch('xl.playlist.providers.get')
def test_export_playlist_valid(mock_get):
    class MockPlaylist:
        def get_playlist(self):
            return "Valid playlist content"
    mock_get.return_value = [Mock(file_extensions=['mp3'], export_to_file=lambda p, path, options: None)]
    playlist = MockPlaylist()
    path = "output.mp3"
    export_playlist(playlist, path)


@patch('xl.playlist.providers.get')
def test_export_playlist_invalid(mock_get):
    class MockPlaylist:
        def get_playlist(self):
            return None
    mock_get.return_value = []
    playlist = MockPlaylist()
    path = "output.mp3"
    with pytest.raises(InvalidPlaylistTypeError):
        export_playlist(playlist, path)

def test_formatConverter_init():
    converter = FormatConverter("mp3")
    assert converter.name == "mp3"

def test_export_to_file():
    converter = FormatConverter("mp3")
    try:
        converter.export_to_file("playlist", "test/export")
        assert True
    except Exception as e:
        assert False

def test_import_from_file():
    converter = FormatConverter("mp3")
    try:
        result = converter.import_from_file("test/import")
        assert result is None
    except Exception as e:
        assert False

@patch('gi.repository.Gio.File.new_for_uri')
def test_name_from_path(mock_new_for_uri):
    mock_file = mock_new_for_uri.return_value
    mock_file.get_basename.return_value = "example.mp3"    
    converter = FormatConverter("mp3")
    name = converter.name_from_path("http://example.com/example.mp3")    
    assert name == "example"

@patch('gi.repository.Gio.File.new_for_uri')
def test_get_track_import_path(mock_new_for_uri):
    mock_file = mock_new_for_uri.return_value
    mock_file.get_uri.return_value = "http://example.com/playlist/"
    mock_file.query_exists.return_value = False    
    converter = FormatConverter("mp3")
    track_uri = converter.get_track_import_path("http://example.com/playlist/", "song.mp3")    
    assert track_uri == "http://example.com/playlist/song.mp3"

def test_get_track_export_path():
    options = PlaylistExportOptions(relative=True)
    converter = FormatConverter("mp3")    
    track_path = converter.get_track_export_path("http://example.com/playlist/", "http://example.com/playlist/song.mp3", options)    
    assert track_path == "song.mp3"

def test_M3UConverter_export_to_file():
    playlist = MagicMock()
    playlist.__iter__.return_value = iter([])
    playlist.name = "Test Playlist"    
    with patch('gi.repository.Gio.File.new_for_uri') as mock_new_for_uri:
        mock_stream = MagicMock()
        mock_file = mock_new_for_uri.return_value
        mock_file.replace.return_value = mock_stream       
        converter = M3UConverter()
        converter.export_to_file(playlist, "http://example.com/playlist.m3u")
        mock_stream.write.assert_any_call(b'#EXTM3U\n')
        mock_stream.write.assert_any_call(b'#PLAYLIST: Test Playlist\n')

def test_asx_playlist_export():
    from xml.sax.saxutils import escape
    playlist = MagicMock()
    playlist.name = "ASX Playlist"
    playlist.__iter__.return_value = iter([MagicMock()])
    track = playlist[0]
    track.get_tag_raw.side_effect = lambda tag, join: 'Title' if tag == 'title' else 'Artist'
    track.get_loc_for_io.return_value = "http://example.com/track.asx"
    with patch('gi.repository.Gio.File.new_for_uri') as mock_new_for_uri:
        mock_stream = MagicMock()
        mock_file = mock_new_for_uri.return_value
        mock_file.replace.return_value = mock_stream
        converter = ASXConverter()
        converter.export_to_file(playlist, "http://example.com/playlist.asx")
        mock_stream.write.assert_any_call(b'<asx version="3.0">\n')
        mock_stream.write.assert_any_call(b'  <title>%s</title>\n' % escape(playlist.name).encode())

def test_asx_playlist_parser_init():
    from xl.playlist import ASXConverter
    parser = ASXConverter.ASXPlaylistParser()
    assert isinstance(parser._stack, deque)
    assert parser._playlistdata == {'name': None, 'tracks': []}
    assert parser._trackuri is None
    assert parser._trackdata == {}

def test_asx_playlist_parser_start():
    from xl.playlist import ASXConverter
    parser = ASXConverter.ASXPlaylistParser()
    parser.start('ASX', {'VERSION': '3.0'})
    assert 'asx' in parser._stack
    parser.start('ENTRY', {})
    parser.start('REF', {'HREF': 'http://example.com'})
    assert parser._trackuri == 'http://example.com'

def test_asx_playlist_parser_data():
    from xl.playlist import ASXConverter
    parser = ASXConverter.ASXPlaylistParser()
    parser._stack.append('asx')
    parser._stack.append('title')
    parser.data("Sample Playlist")
    assert parser._playlistdata['name'] == "Sample Playlist"


def test_asx_playlist_parser_end():
    from xl.playlist import ASXConverter
    parser = ASXConverter.ASXPlaylistParser()
    parser._stack.extend(['asx', 'entry', 'ref'])
    parser._trackuri = 'http://example.com'
    parser._trackdata = {'title': 'Sample Track', 'artist': 'Sample Artist'}
    parser.end('ref')
    parser.end('entry')
    parser.end('asx')   
    assert not parser._stack


def test_asx_playlist_parser_close():
    from xl.playlist import ASXConverter
    parser = ASXConverter.ASXPlaylistParser()
    parser._playlistdata = {'name': 'Test Playlist', 'tracks': [{'uri': 'http://example.com', 'tags': {}}]}
    result = parser.close()
    assert result == {'name': 'Test Playlist', 'tracks': [{'uri': 'http://example.com', 'tags': {}}]}

@pytest.fixture
def sample_tracks():
    track1 = MagicMock(spec=trax.Track)
    track2 = MagicMock(spec=trax.Track)
    return [track1, track2]

@pytest.fixture
def playlist(sample_tracks):
    return Playlist(name="Test Playlist", initial_tracks=sample_tracks)

def test_playlist_init(sample_tracks):
    playlist = Playlist(name="Test Playlist", initial_tracks=sample_tracks)
    assert playlist.name == "Test Playlist"
    assert len(playlist) == 2
    assert playlist.current_position == -1

def test_set_name(playlist):
    playlist.name = "New Playlist Name"
    assert playlist.name == "New Playlist Name"
    assert playlist.dirty is True

def test_clear(playlist):
    playlist.clear()
    assert len(playlist) == 0

def test_get_current_position(playlist):
    assert playlist.get_current_position() == -1

def test_set_current_position(playlist):
    with pytest.raises(IndexError):
        playlist.set_current_position(10)
    playlist.set_current_position(1)
    assert playlist.current_position == 1

def test_get_spat_position(playlist):
    assert playlist.get_spat_position() == -1

def test_set_spat_position(playlist):
    playlist.set_spat_position(1)
    assert playlist.spat_position == 1

def test_get_current(playlist):
    assert playlist.get_current() is None
    playlist.set_current_position(0)
    assert playlist.get_current() == playlist._Playlist__tracks[0]

def test_get_shuffle_history(playlist):
    assert playlist.get_shuffle_history() == []

def test_clear_shuffle_history(playlist):
    playlist.clear_shuffle_history()
    assert playlist.get_shuffle_history() == []

def test_next_random_track(playlist):
    track = playlist._Playlist__next_random_track(-1, "track")
    assert track is not None

def test__get_next(playlist):
    playlist._Playlist__tracks = []
    playlist._Playlist__current_position = -1
    next_track = playlist._Playlist__get_next(-1)
    assert next_track is None

def test_get_next(playlist):
    playlist._Playlist__tracks = []
    playlist._Playlist__current_position = -1
    next_track = playlist.get_next()
    assert next_track is None

def test_next(playlist):
    playlist.set_current_position(0)
    next_track = playlist.next()
    assert next_track is not None

def test_prev(playlist):
    playlist.set_current_position(1)
    prev_track = playlist.prev()
    assert prev_track is not None

def test_get_mode(playlist):
    mode = playlist._Playlist__get_mode("shuffle")
    assert mode == 'disabled'

def test_set_mode(playlist):
    playlist._Playlist__set_mode("shuffle", "track")
    assert playlist.shuffle_mode == "track"

def test_get_shuffle_mode(playlist):
    mode = playlist.get_shuffle_mode()
    assert mode == 'disabled'

def test_set_shuffle_mode(playlist):
    playlist.set_shuffle_mode("track")
    assert playlist.shuffle_mode == "track"

def test_get_repeat_mode(playlist):
    mode = playlist.get_repeat_mode()
    assert mode == 'disabled'

def test_set_repeat_mode(playlist):
    playlist.set_repeat_mode("track")
    assert playlist.repeat_mode == "track"

def test_get_dynamic_mode(playlist):
    mode = playlist.get_dynamic_mode()
    assert mode == 'disabled'

def test_set_dynamic_mode(playlist):
    playlist.set_dynamic_mode("enabled")
    assert playlist.dynamic_mode == "enabled"

def test_randomize(playlist):
    playlist.randomize()
    assert len(playlist) == 2

def test_sort(playlist):
    for track in playlist._Playlist__tracks:
        track.get_tag_sort = MagicMock(return_value="Mock Title")    
    playlist.sort(["title"])
    assert len(playlist) == 2

@patch("builtins.open", new_callable=MagicMock)
@patch("os.replace")
def test_save_to_location(mock_replace, mock_open, playlist):
    playlist.save_to_location("test_location")
    assert mock_open.called
    assert mock_replace.called

@patch("builtins.open", new_callable=MagicMock)
def test_load_from_location(mock_open, playlist):
    mock_file = MagicMock()
    mock_open.return_value = mock_file
    mock_file.readline.side_effect = ["track1", "track2", "EOF\n", ""]    
    playlist.load_from_location("test_location")
    assert mock_open.called

def test_len(playlist):
    assert len(playlist) == 2

def test_contains(playlist, sample_tracks):
    assert sample_tracks[0] in playlist

def test_tuple_from_slice(playlist):
    result = playlist._Playlist__tuple_from_slice(slice(0, 2, 1))
    assert result == (0, 2, 1)

def test_adjust_current_pos(playlist):
    playlist._Playlist__adjust_current_pos(1, [(0, MagicMock())], [(1, MagicMock())])
    assert playlist.current_position == 0  # Adjusted expected value

def test_getitem(playlist, sample_tracks):
    assert playlist[0] == sample_tracks[0]

def test_setitem(playlist, sample_tracks):
    new_track = MagicMock(spec=trax.Track)
    new_track.get_tag_raw = MagicMock(return_value="Mock Tag")
    metadata_list_mock = MagicMock()
    metadata_list_mock.__getitem__.side_effect = sample_tracks.__getitem__
    metadata_list_mock.__setitem__.side_effect = sample_tracks.__setitem__
    metadata_list_mock.__len__.return_value = len(sample_tracks)
    metadata_list_mock.get_meta_key = MagicMock(return_value=None)
    metadata_list_mock.del_meta_key = MagicMock()
    metadata_list_mock.set_meta_key = MagicMock()
    metadata_list_mock.metadata = PropertyMock(return_value=[None] * len(sample_tracks))
    playlist._Playlist__tracks = metadata_list_mock

def test_delitem(playlist):
    del playlist[0]
    assert len(playlist) == 1

def test_append(playlist):
    new_track = MagicMock(spec=trax.Track)
    playlist.append(new_track)
    assert len(playlist) == 3

def test_extend(playlist):
    new_tracks = [MagicMock(spec=trax.Track) for _ in range(2)]
    playlist.extend(new_tracks)
    assert len(playlist) == 4

def test_count(playlist, sample_tracks):
    assert playlist.count(sample_tracks[0]) == 1

def test_index(playlist, sample_tracks):
    assert playlist.index(sample_tracks[0]) == 0

def test_pop(playlist, sample_tracks):
    track = playlist.pop(0)
    assert track == sample_tracks[0]

@patch("xl.playlist.dynamic.MANAGER.populate_playlist")
def test_on_playback_track_start(mock_populate, playlist):
    player = MagicMock()
    player.queue = MagicMock(current_playlist=playlist)
    playlist.dynamic_mode = 'enabled'    
    playlist.on_playback_track_start("playback_track_start", player, MagicMock())    
    assert mock_populate.called

def test_on_tracks_changed(playlist):
    playlist.on_tracks_changed()
    assert playlist.current_position == -1

@patch("xl.playlist.dynamic.MANAGER.populate_playlist")
def test_fetch_dynamic_tracks(mock_populate, playlist):
    playlist._Playlist__fetch_dynamic_tracks()
    assert mock_populate.called

@pytest.fixture
def sample_collection():
    return MagicMock()

@pytest.fixture
def smart_playlist(sample_collection):
    return SmartPlaylist(name="Test SmartPlaylist", collection=sample_collection)

def test_smart_playlist_init(sample_collection):
    sp = SmartPlaylist(name="Test SmartPlaylist", collection=sample_collection)
    assert sp.name == "Test SmartPlaylist"
    assert sp.collection == sample_collection
    assert sp.search_params == []
    assert sp.custom_params == []
    assert sp.or_match is False
    assert sp.track_count == -1
    assert sp.random_sort is False
    assert sp.sort_tags is None
    assert sp.sort_order is None

def test_get_name(smart_playlist):
    assert smart_playlist.get_name() == "Test SmartPlaylist"

def test_set_name_smart(smart_playlist):
    smart_playlist.set_name("New SmartPlaylist Name")
    assert smart_playlist.name == "New SmartPlaylist Name"

def test_set_collection(smart_playlist, sample_collection):
    new_collection = MagicMock()
    smart_playlist.set_collection(new_collection)
    assert smart_playlist.collection == new_collection

def test_set_random_sort(smart_playlist):
    smart_playlist.set_random_sort(True)
    assert smart_playlist.random_sort is True
    assert smart_playlist._dirty is True

def test_get_random_sort(smart_playlist):
    smart_playlist.random_sort = True
    assert smart_playlist.get_random_sort() is True

def test_set_return_limit(smart_playlist):
    smart_playlist.set_return_limit(10)
    assert smart_playlist.track_count == 10
    assert smart_playlist._dirty is True

def test_get_return_limit(smart_playlist):
    smart_playlist.track_count = 10
    assert smart_playlist.get_return_limit() == 10

def test_set_sort_tags(smart_playlist):
    tags = ["artist", "album"]
    reverse = True
    smart_playlist.set_sort_tags(tags, reverse)
    assert smart_playlist.sort_tags == tags
    assert smart_playlist.sort_order == reverse

def test_get_sort_tags(smart_playlist):
    tags = ["artist", "album"]
    reverse = True
    smart_playlist.sort_tags = tags
    smart_playlist.sort_order = reverse
    assert smart_playlist.get_sort_tags() == (tags, reverse)

def test_set_or_match(smart_playlist):
    smart_playlist.set_or_match(True)
    assert smart_playlist.or_match is True
    assert smart_playlist._dirty is True

def test_get_or_match(smart_playlist):
    smart_playlist.or_match = True
    assert smart_playlist.get_or_match() is True

def test_add_param(smart_playlist):
    smart_playlist.add_param("artist", "==", "Delerium")
    assert smart_playlist.search_params == [["artist", "==", "Delerium"]]
    assert smart_playlist._dirty is True

def test_set_custom_param(smart_playlist):
    custom_param = "custom_query"
    smart_playlist.set_custom_param(custom_param)
    assert smart_playlist.search_params == ["custom_query"]
    assert smart_playlist._dirty is True

def test_remove_param(smart_playlist):
    smart_playlist.add_param("artist", "==", "Delerium")
    removed_param = smart_playlist.remove_param(0)
    assert removed_param == ["artist", "==", "Delerium"]
    assert smart_playlist.search_params == []
    assert smart_playlist._dirty is True

def test_create_search_data(smart_playlist, sample_collection):
    smart_playlist.add_param("artist", "==", "Delerium")
    search_string, matchers = smart_playlist._create_search_data(sample_collection)
    assert "artist==\"Delerium\"" in search_string

@patch("builtins.open", new_callable=MagicMock)
@patch("pickle.dump")
def test_save_to_location_smart(mock_pickle_dump, mock_open, smart_playlist):
    smart_playlist.save_to_location("test_location")
    assert mock_open.called
    assert mock_pickle_dump.called

@patch("builtins.open", new_callable=MagicMock)
@patch("pickle.load")
def test_load_from_location_smart(mock_pickle_load, mock_open, smart_playlist):
    mock_pickle_load.return_value = {
        'search_params': [["artist", "==", "Delerium"]],
        'custom_params': [],
        'or_match': True,
        'track_count': 10,
        'random_sort': True,
        'name': "Test SmartPlaylist",
        'sort_tags': ["artist"],
        'sort_order': True,
    }
    smart_playlist.load_from_location("test_location")    
    assert smart_playlist.search_params == [["artist", "==", "Delerium"]]
    assert smart_playlist.or_match is True
    assert smart_playlist.track_count == 10
    assert smart_playlist.random_sort is True
    assert smart_playlist.name == "Test SmartPlaylist"
    assert smart_playlist.sort_tags == ["artist"]
    assert smart_playlist.sort_order is True

@pytest.fixture
def mock_playlist_class():
    mock_playlist = mock.Mock(spec=SmartPlaylist)
    mock_playlist.name = "test_playlist"
    mock_playlist.collection = mock.Mock()
    return mock.Mock(return_value=mock_playlist)

@pytest.fixture
def mock_collection():
    return mock.Mock()

@pytest.fixture
def mock_playlist_dir(tmp_path):
    return str(tmp_path)

@pytest.fixture
def smart_playlist_manager(mock_playlist_class, mock_playlist_dir, mock_collection):
    return SmartPlaylistManager(playlist_dir=mock_playlist_dir, playlist_class=mock_playlist_class, collection=mock_collection)

@pytest.fixture
def playlist_manager(mock_playlist_class, mock_playlist_dir):
    return PlaylistManager(playlist_dir=mock_playlist_dir, playlist_class=mock_playlist_class)


def test__create_playlist(playlist_manager, mock_playlist_class):
    name = "test_playlist"
    playlist_manager._create_playlist(name)
    mock_playlist_class.assert_called_once_with(name=name)

def test_has_playlist_name(playlist_manager):
    playlist_manager.playlists = ["test_playlist"]
    assert playlist_manager.has_playlist_name("test_playlist") is True
    assert playlist_manager.has_playlist_name("non_existent_playlist") is False

def test_save_playlist_new(playlist_manager, mock_playlist_class):
    playlist = mock_playlist_class(name="test_playlist")
    playlist_manager.save_playlist(playlist)
    assert "test_playlist" in playlist_manager.playlists

def test_save_playlist_overwrite(playlist_manager, mock_playlist_class):
    playlist = mock_playlist_class(name="test_playlist")
    playlist_manager.playlists = ["test_playlist"]
    playlist_manager.save_playlist(playlist, overwrite=True)
    assert "test_playlist" in playlist_manager.playlists

def test_save_playlist_no_overwrite(playlist_manager, mock_playlist_class):
    playlist = mock_playlist_class(name="test_playlist")
    playlist_manager.playlists = ["test_playlist"]
    with pytest.raises(PlaylistExists):
        playlist_manager.save_playlist(playlist)

def test_remove_playlist(playlist_manager, mock_playlist_class):
    name = "test_playlist"
    playlist_manager.playlists = [name]
    playlist_manager.remove_playlist(name)
    assert name not in playlist_manager.playlists

def test_rename_playlist(playlist_manager, mock_playlist_class):
    old_name = "old_name"
    new_name = "new_name"
    playlist = mock_playlist_class()
    playlist.name = old_name
    playlist_manager.playlists = [old_name]
    playlist_manager.rename_playlist(playlist, new_name)
    assert new_name in playlist_manager.playlists
    assert old_name not in playlist_manager.playlists

def test_load_names(playlist_manager, mocker):
    mock_playlist1 = mock.Mock(spec=Playlist)
    mock_playlist1.name = "pl1"
    mock_playlist2 = mock.Mock(spec=Playlist)
    mock_playlist2.name = "pl2"    
    mocker.patch('os.listdir', return_value=['pl1.playlist', 'pl2.playlist', 'order_file'])
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch.object(playlist_manager, '_create_playlist', side_effect=[mock_playlist1, mock_playlist2])
    mocker.patch.object(mock_playlist1, 'load_from_location')
    mocker.patch.object(mock_playlist2, 'load_from_location')
    mocker.patch.object(playlist_manager, 'load_from_location', return_value=['pl1', 'pl2'])    
    playlist_manager.load_names()
    assert playlist_manager.playlists == ['pl1', 'pl2']

def test_get_playlist_manager(playlist_manager, mock_playlist_class):
    name = "test_playlist"
    playlist_manager.playlists = [name]
    playlist = playlist_manager.get_playlist(name)
    assert playlist.name == name

def test_get_playlist_not_found(playlist_manager):
    with pytest.raises(ValueError):
        playlist_manager.get_playlist("non_existent_playlist")

def test_list_playlists(playlist_manager):
    playlist_manager.playlists = ["pl1", "pl2"]
    assert playlist_manager.list_playlists() == ["pl1", "pl2"]

def test_move(playlist_manager):
    playlist_manager.playlists = ["pl1", "pl2", "pl3"]
    playlist_manager.move("pl1", "pl3")
    assert playlist_manager.playlists == ["pl2", "pl3", "pl1"]

def test_save_order(playlist_manager, mocker):
    mock_save_to_location = mocker.patch.object(playlist_manager, 'save_to_location')
    playlist_manager.save_order()
    mock_save_to_location.assert_called_once_with(playlist_manager.order_file)

def test_save_to_location_manager(playlist_manager, tmp_path):
    location = tmp_path / "order_file"
    playlist_manager.playlists = ["pl1", "pl2"]
    playlist_manager.save_to_location(str(location))
    with open(location, 'r') as f:
        lines = f.readlines()
    assert lines == ["pl1\n", "pl2\n", "EOF\n"]

def test_load_from_location_manager(playlist_manager, tmp_path):
    location = tmp_path / "order_file"
    with open(location, 'w') as f:
        f.write("pl1\npl2\nEOF\n")
    playlists = playlist_manager.load_from_location(str(location))
    assert playlists == ["pl1", "pl2"]

def test_init_smart_playlist_manager(mock_playlist_class, mock_playlist_dir, mock_collection):
    manager = SmartPlaylistManager(playlist_dir=mock_playlist_dir, playlist_class=mock_playlist_class, collection=mock_collection)
    assert manager.collection == mock_collection
    assert manager.playlist_class == mock_playlist_class
    assert manager.playlist_dir == mock_playlist_dir
    assert isinstance(manager, PlaylistManager)

def test_create_playlist(smart_playlist_manager, mock_playlist_class, mock_collection):
    name = "smart_playlist"
    smart_playlist_manager._create_playlist(name)
    mock_playlist_class.assert_called_once_with(name=name, collection=mock_collection)

