import pytest
from unittest.mock import MagicMock

from xl.player.queue import PlayQueue

@pytest.fixture
def player():
    return MagicMock()


@pytest.fixture
def queue(player):
    return PlayQueue(player, "queue")


def test_set_current_playlist(queue):
    playlist = MagicMock()

    queue.set_current_playlist(playlist)

    assert queue.current_playlist == playlist

def test_set_current_playlist_none(queue):
    queue.set_current_playlist(None)

    assert queue.current_playlist == queue


def test_get_next_with_queue(queue):
    queue._calculate_next_track = MagicMock(return_value="track")

    queue.set_current_playlist(queue)

    next_track = queue.get_next()

    assert next_track == "track"


def test_get_next_with_playlist(queue):
    playlist_mock = MagicMock()
    playlist_mock.get_next = MagicMock(return_value="next_track_in_playlist")
    queue.set_current_playlist(playlist_mock)

    next_track = queue.get_next()

    assert next_track == "next_track_in_playlist"


def test_next_with_remove_item_on_playback(queue):
    queue._calculate_next_track = MagicMock(return_value="next_track_in_queue")
    queue.pop = MagicMock()
    queue._PlayQueue__remove_item_on_playback = True
    
    queue.set_current_playlist(queue)

    queue.next()

    queue.pop.assert_called_once()
