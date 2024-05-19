from unittest.mock import MagicMock

from xl.migrations.database.covers_1to2 import old_get_track_key


def test_old_get_track_key_with_album():
    track_mock = MagicMock()
    track_mock.get_tag_raw.return_value = "Some Album"
    key = old_get_track_key(track_mock)
    assert key == ('albumartist', ('S', 'o', 'm', 'e', ' ', 'A', 'l', 'b', 'u', 'm'))

def test_old_get_track_key_with_compilation():
    track_mock = MagicMock()
    track_mock.get_tag_raw.return_value = None
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "Various Artists" if tag == 'albumartist' else False
    key = old_get_track_key(track_mock)
    assert key == None

def test_old_get_track_key_without_album_info():
    track_mock = MagicMock()
    track_mock.get_tag_raw.return_value = None
    key = old_get_track_key(track_mock)
    assert key is None
    
def test_old_get_track_key_with_albumartist():
    track_mock = MagicMock()
    track_mock.get_tag_raw.return_value = None
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "Various Artists" if tag == 'albumartist' else False
    key = old_get_track_key(track_mock)
    assert key == None

def test_old_get_track_key_with_album_and_albumartist():
    track_mock = MagicMock()
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "Some Album" if tag == 'album' else ("Various Artists" if tag == 'albumartist' else False)
    key = old_get_track_key(track_mock)
    assert key ==('album', ('S', 'o', 'm', 'e', ' ', 'A', 'l', 'b', 'u', 'm'))
    
def test_old_get_track_key_with_compilation_and_no_albumartist():
    track_mock = MagicMock()
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "1" if tag == '__compilation' else None
    key = old_get_track_key(track_mock)
    assert key == ('compilation', ('1',))

def test_old_get_track_key_with_empty_compilation():
    track_mock = MagicMock()
    track_mock.get_tag_raw.return_value = None
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "" if tag == '__compilation' else False
    key = old_get_track_key(track_mock)
    assert key is None

def test_old_get_track_key_with_compilation_and_albumartist():
    track_mock = MagicMock()
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "Various Artists" if tag == 'albumartist' else "1" if tag == '__compilation' else False
    key = old_get_track_key(track_mock)
    assert key == ('albumartist', ('V', 'a', 'r', 'i', 'o', 'u', 's', ' ', 'A', 'r', 't', 'i', 's', 't', 's'))

def test_old_get_track_key_with_album_and_empty_albumartist():
    track_mock = MagicMock()
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "Some Album" if tag == 'album' else "" if tag == 'albumartist' else False
    key = old_get_track_key(track_mock)
    assert key == ('album', ('S', 'o', 'm', 'e', ' ', 'A', 'l', 'b', 'u', 'm'))

def test_old_get_track_key_with_compilation_and_empty_albumartist():
    track_mock = MagicMock()
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "" if tag == 'albumartist' else "1" if tag == '__compilation' else False
    key = old_get_track_key(track_mock)
    assert key == ('compilation', ('1',))

def test_old_get_track_key_with_empty_album_and_albumartist():
    track_mock = MagicMock()
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "" if tag == 'album' else "Various Artists" if tag == 'albumartist' else False
    key = old_get_track_key(track_mock)
    assert key == None

def test_old_get_track_key_with_album_and_empty_compilation():
    track_mock = MagicMock()
    track_mock.get_tag_raw.side_effect = lambda tag, join=True: "" if tag == '__compilation' else "Some Album" if tag == 'album' else False
    key = old_get_track_key(track_mock)
    assert key == ('album', ('S', 'o', 'm', 'e', ' ', 'A', 'l', 'b', 'u', 'm'))