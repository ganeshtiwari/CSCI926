from unittest.mock import MagicMock
import pytest
from xl.player.player import ExailePlayer
from xl.trax.track import Track

@pytest.fixture
def player():
    return ExailePlayer("player")

@pytest.fixture
def track():
    track = MagicMock()
    track.__class__ = Track
    return track

def test_get_volume(player):
    assert player.get_volume() == 100

def test_set_volume_negative(player):
    player.set_volume(-10)
    assert player.get_volume() == 0

def test_set_volume_0(player):
    player.set_volume(0)
    assert player.get_volume() == 0


def test_set_volume_min_positive(player):
    player.set_volume(1)
    assert player.get_volume() == 1

def test_set_volume(player):
    player.set_volume(50)
    assert player.get_volume() == 50

def test_modify_volume(player):
    player.modify_volume(1)
    assert player.get_volume() == 51

def test_get_position(player):
    assert player.get_position() == 0

def test_get_state(player):
    assert player.get_state() == "stopped"

def test_is_playing(player):
    assert not player.is_playing()

def test_is_paused(player):
    assert not player.is_paused()

def test_is_stopped(player):
    assert player.is_stopped()
    
def test_play_no_track(player):
    player.stop = MagicMock()
    
    player.play(track=None)
    
    player.stop.assert_called_once()
 
# def test_play_track(player, track):
#     player._get_play_params = MagicMock(return_value=(track, 2, False, False, False))
    
#     assert True
    # play_args = self._get_play_params(track, start_at, paused, False, False)
    # track.get_tag_raw.return_value = None

    # player.play(track)

    # assert engine
