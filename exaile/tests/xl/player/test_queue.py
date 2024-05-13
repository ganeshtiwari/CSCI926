import pytest
from unittest.mock import MagicMock, patch

from xl.trax.track import Track
from xl.player.queue import PlayQueue

@pytest.fixture
def player():
    return MagicMock()


@pytest.fixture
def play_queue(player):
    return PlayQueue(player, "queue")

def test_set_current_playlist(play_queue):
    playlist_mock = MagicMock()

    play_queue.set_current_playlist(playlist_mock)

    assert play_queue._PlayQueue__current_playlist == playlist_mock

def test_set_current_playlist_with_none(play_queue):

    play_queue.set_current_playlist(None)

    assert play_queue._PlayQueue__current_playlist == play_queue
    assert play_queue._PlayQueue__queue_has_tracks == True

def test_current_playlist_getter(play_queue):
    playlist_mock = MagicMock()
    play_queue._PlayQueue__current_playlist = playlist_mock
    
    assert play_queue.current_playlist == playlist_mock

def test_get_next_with_queue_has_tracks(play_queue):
    with patch("xl.player.queue.len", return_value=1) as mocked_len: 
        
        play_queue._PlayQueue__queue_has_tracks = True

        track = MagicMock()
        play_queue._calculate_next_track = MagicMock(return_value=track)

        assert play_queue.get_next() == track
        mocked_len.assert_called_once()

def test_get_next_with_current_playlist(play_queue):
    playlist_mock = MagicMock()
    play_queue._PlayQueue__current_playlist = playlist_mock

    track_mock = MagicMock()
    playlist_mock.get_next = MagicMock(return_value=track_mock)

    assert play_queue.get_next() == track_mock

def test_get_next_with_last_playlist(play_queue):
    last_playlist_mock = MagicMock()
    play_queue.last_playlist = last_playlist_mock

    track_mock = MagicMock()
    last_playlist_mock.get_next = MagicMock(return_value=track_mock)

    assert play_queue.get_next() == track_mock

# TODO: Publish Issue
# def test_get_next_with_no_tracks(play_queue):
#     play_queue._PlayQueue__queue_has_tracks = False
#     play_queue._PlayQueue__current_playlist = None
#     play_queue.last_playlist = None
    
#     assert play_queue.get_next() == None
    
# def test_next_autoplay_true_with_remove_after_playback_true(play_queue):
#     # Set up the queue with tracks and necessary flags
#     play_queue._PlayQueue__queue_has_tracks = True
#     play_queue._PlayQueue__remove_item_on_playback = True
#     play_queue._PlayQueue__remove_item_after_playback = True

#     track_mock = MagicMock()
#     play_queue._calculate_next_track = MagicMock(return_value=track_mock)

#     returned_track = play_queue.next(autoplay=True)

#     play_queue.player.play.assert_called_once_with(track_mock)

#     play_queue.pop.assert_called_once_with(play_queue.current_position)

#     assert play_queue.current_position == 0

def test_next_autoplay_true_with_remove_after_playback_false(play_queue):

    play_queue._PlayQueue__queue_has_tracks = True
    play_queue._PlayQueue__remove_item_on_playback = True
    play_queue._PlayQueue__remove_item_after_playback = False

    track_mock = MagicMock()
    play_queue.pop = MagicMock(return_value=track_mock)

    returned_track = play_queue.next(autoplay=True)

    play_queue.player.play.assert_called_once_with(track_mock)

    play_queue.pop.assert_called_once_with(0)

    assert play_queue.current_position == -1

def test_prev_with_current_track_less_than_5_seconds(play_queue):
    play_queue.player.current = MagicMock()
    play_queue.player.get_time.return_value = 4
    play_queue._PlayQueue__queue_has_tracks = True
    play_queue._PlayQueue__remove_item_on_playback = False

    returned_track = play_queue.prev()

    play_queue.player.play.assert_called_once()

def test_prev_with_current_track_with_2_seconds(play_queue):
    play_queue.player.current = MagicMock()
    play_queue.player.get_time.return_value = 2
    play_queue._PlayQueue__queue_has_tracks = True
    play_queue._PlayQueue__remove_item_on_playback = False

    returned_track = play_queue.prev()

    play_queue.player.play.assert_called_once()

def test_prev_with_current_track_more_than_5_seconds(play_queue):
    play_queue.player.current = MagicMock()
    play_queue.player.get_time.return_value = 6
    play_queue._PlayQueue__queue_has_tracks = True
    play_queue._PlayQueue__remove_item_on_playback = False

    returned_track = play_queue.prev()

    play_queue.player.play.assert_called_once()
    assert returned_track == play_queue.player.current

def test_prev_with_current_track_with_10_seconds(play_queue):
    play_queue.player.current = MagicMock()
    play_queue.player.get_time.return_value = 10
    play_queue._PlayQueue__queue_has_tracks = True
    play_queue._PlayQueue__remove_item_on_playback = False

    returned_track = play_queue.prev()

    play_queue.player.play.assert_called_once()
    assert returned_track == play_queue.player.current
    
# TODO: Test for get_current

def test_get_next_with_playlist(play_queue):
    playlist_mock = MagicMock()
    playlist_mock.get_next = MagicMock(return_value="next_track_in_playlist")
    play_queue.set_current_playlist(playlist_mock)

    next_track = play_queue.get_next()

    assert next_track == "next_track_in_playlist"

def test_next_with_remove_item_on_playback(play_queue):
    play_queue._calculate_next_track = MagicMock(return_value="next_track_in_queue")
    play_queue.pop = MagicMock()
    play_queue._PlayQueue__remove_item_on_playback = True
    
    play_queue.set_current_playlist(play_queue)

    play_queue.next()

    play_queue.pop.assert_not_called()
    
def test_is_play_enabled_when_playing(play_queue):

    play_queue.player.is_playing = MagicMock(return_value=False)
    play_queue._PlayQueue__disable_new_track_when_playing = True
    result = play_queue.is_play_enabled()
    assert result == True


def test_is_play_enabled_when_playing_1(play_queue):
    play_queue.player.is_playing = MagicMock(return_value=True)

    play_queue._PlayQueue__disable_new_track_when_playing = True

    result = play_queue.is_play_enabled()

    assert result == False

def test_play_with_no_track(play_queue):
    play_queue.player.is_playing = MagicMock(return_value=True)

    play_queue.play()

    assert play_queue.player.play.call_count == 0


def test_play_returns_without_playing_when_playing_true_1(play_queue):
    play_queue.player.is_playing = MagicMock(return_value=True)

    play_queue._PlayQueue__disable_new_track_when_playing = True

    play_queue.play()

    assert play_queue.player.play.call_count == 0


def test_play_plays_provided_track(play_queue):
    mock_track = MagicMock()

    play_queue.play(track=mock_track)

    play_queue.player.play.assert_called_once_with(mock_track)

def test_queue_length_remove_item_on(play_queue):
    track1 = MagicMock()
    track2 = MagicMock()
    
    track1.__class__ = Track
    track2.__class__ = Track
    
    play_queue._PlayQueue__remove_item_on_playback = True
    play_queue.append(track1)
    play_queue.append(track2)
    assert play_queue.queue_length() == 2

def test_queue_length_no_tracks(play_queue):

    play_queue._PlayQueue__remove_item_on_playback = False

    play_queue._PlayQueue__queue_has_tracks = False

    assert play_queue.queue_length() == -1

def test_queue_length_with_tracks(play_queue):
    track1 = MagicMock()
    track2 = MagicMock()
    
    track1.__class__ = Track
    track2.__class__ = Track
    
    play_queue._PlayQueue__remove_item_on_playback = False

    play_queue._PlayQueue__queue_has_tracks = True

    play_queue.append(track1)
    play_queue.append(track2)

    play_queue._PlayQueue__current_position = 1
    assert play_queue.queue_length() == 1
    
def test_calculate_next_track_empty_queue(play_queue):
    assert play_queue._calculate_next_track() is None

def test_calculate_next_track_single_track(play_queue):
    track = MagicMock()
    track.__class__ = Track
    
    play_queue.append(track)
    assert play_queue._calculate_next_track() is track

def test_calculate_next_track_multiple_tracks(play_queue):
    track1 = MagicMock()
    track2 = MagicMock()
    track1.__class__ = Track
    track2.__class__ = Track
    
    play_queue.append(track1)
    play_queue.append(track2)
    assert play_queue._calculate_next_track() == track1

def test_calculate_next_track_playing_track(play_queue):
    track1 = MagicMock()
    track2 = MagicMock()
    track1.__class__ = Track
    track2.__class__ = Track
    
    play_queue.append(track1)
    play_queue.append(track2)
    play_queue.player.current = track1
    assert play_queue._calculate_next_track() == track2