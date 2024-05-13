import pytest
from unittest.mock import MagicMock

from xl.player.track_fader import FadeState, TrackFader

@pytest.fixture
def track_fader():
    # You may need to pass any required arguments to initialize TrackFader
    return TrackFader(MagicMock(), "on_fade_out", "name")

def test_calculate_fades_default(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect

    fade_in, fade_out = None, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)

    assert result == (5, 5, 10, 10)

def test_calculate_fades_default_1(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 5
        elif tag == "__length":
            return 5
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect

    fade_in, fade_out = None, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)

    assert result == (5, 5, 5, 5)

def test_calculate_fades_default_2(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return -1
        elif tag == "__stopoffset":
            return 2
        elif tag == "__length":
            return 2
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect

    fade_in, fade_out = None, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)

    assert result == (-1, -1, 2, 2)

def test_calculate_fades_default_3(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return 1
        elif tag == "__length":
            return 2
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect

    fade_in, fade_out = None, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)

    assert result == (0, 0, 1, 1)

def test_calculate_fades_default_4(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return 0
        elif tag == "__length":
            return 0
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect

    fade_in, fade_out = None, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)

    assert result == (0, 0, 0, 0)

def test_calculate_fades_default_5(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 10 
        elif tag == "__stopoffset":
            return 20
        elif tag == "__length":
            return 30
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect

    fade_in, fade_out = None, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)

    assert result == (10, 10, 20, 20)
    

def test_calculate_fades_with_fade_in(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (5, 7, 10, 10)

def test_calculate_fades_with_fade_in_1(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0
        elif tag == "__stopoffset":
            return 0
        elif tag == "__length":
            return 0
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (0, 0, 0, 0)

def test_calculate_fades_with_fade_in_2(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return 1
        elif tag == "__length":
            return 2
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (0, 1.0, 1.0, 1)

def test_calculate_fades_with_fade_in_3(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 20
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (0, 2, 10, 10)

def test_calculate_fades_with_fade_in_4(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 10 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 10
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (10, 10, 10, 10)
  
def test_calculate_fades_with_fade_in_5(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return -1 
        elif tag == "__stopoffset":
            return -1
        elif tag == "__length":
            return -1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, -1, -1, -1)

def test_calculate_fades_with_fade_in_6(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return -1 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, 1, 10, 10)

def test_calculate_fades_with_fade_in_7(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 3 
        elif tag == "__stopoffset":
            return 4
        elif tag == "__length":
            return 5
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (3, 4.0, 4.0, 4)

def test_calculate_fades_with_fade_in_8(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 1000 
        elif tag == "__stopoffset":
            return 100
        elif tag == "__length":
            return -1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, -1, -1, -1)
    
def test_calculate_fades_with_fade_in_9(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return -1
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, None
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (5, 7, 15, 15)

def test_calculate_fades_with_fade_out(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (5, 5, 8, 10)

def test_calculate_fades_with_fade_out_1(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return 0
        elif tag == "__length":
            return 0
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (0, 0, 0, 0)
  
def test_calculate_fades_with_fade_out_2(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return -1 
        elif tag == "__stopoffset":
            return -1
        elif tag == "__length":
            return -1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, -1, -1, -1)

def test_calculate_fades_with_fade_out_3(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return -1 
        elif tag == "__stopoffset":
            return 0
        elif tag == "__length":
            return 1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, -1, -1, 1)

def test_calculate_fades_with_fade_out_4(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 1 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 20
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (1, 1, 8, 10)

def test_calculate_fades_with_fade_out_5(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 1000 
        elif tag == "__stopoffset":
            return 0
        elif tag == "__length":
            return 1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (1, 1, 1, 1)

def test_calculate_fades_with_fade_out_6(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 2 
        elif tag == "__stopoffset":
            return 3
        elif tag == "__length":
            return 4
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (2, 2.0, 2.0, 3)

def test_calculate_fades_with_fade_out_7(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return 0
        elif tag == "__length":
            return -1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = None, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, -1, -1, -1)

def test_calculate_fades_with_fade_in_out(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (5, 7, 8, 10)

def test_calculate_fades_with_fade_in_out_1(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (5, 7, 8, 10)

def test_calculate_fades_with_fade_in_out_2(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (5, 7, 8, 10)

def test_calculate_fades_with_fade_in_out_3(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return -1
        elif tag == "__length":
            return -1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, -1, -1, -1)

def test_calculate_fades_with_fade_in_out_4(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 1 
        elif tag == "__stopoffset":
            return 2
        elif tag == "__length":
            return 3
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (1, 1.5, 1.5, 2)

def test_calculate_fades_with_fade_in_out_5(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return -1
        elif tag == "__length":
            return 0
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (0, 0, 0, 0)

def test_calculate_fades_with_fade_in_out_6(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return -1 
        elif tag == "__stopoffset":
            return -1
        elif tag == "__length":
            return -1
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (-1, -1, -1, -1)

def test_calculate_fades_with_fade_in_out_7(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 0 
        elif tag == "__stopoffset":
            return 0
        elif tag == "__length":
            return 0
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = 2, 2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (0, 0, 0, 0)
    
def test_calculate_fades_with_negative_fades(track_fader):
    track = MagicMock(spec=["get_tag_raw"])

    def get_tag_raw_side_effect(tag):
        if tag == "__startoffset":
            return 5 
        elif tag == "__stopoffset":
            return 10
        elif tag == "__length":
            return 15
    
    track.get_tag_raw.side_effect = get_tag_raw_side_effect
    
    fade_in, fade_out = -2, -2
    result = track_fader.calculate_fades(track, fade_in, fade_out)
    assert result == (5, 5, 10, 10)

def test_user_volume_zero_fade_volume(track_fader):
    track_fader.fade_volume = 0.0
    track_fader.user_volume = 0.5
    real_volume = 0.8
    result, is_same = track_fader.calculate_user_volume(real_volume)
    assert result == real_volume
    assert is_same == True

def test_user_volume_nonzero_fade_volume(track_fader):
    track_fader.fade_volume = 0.8
    track_fader.user_volume = 0.6
    real_volume = 0.5
    result, is_same = track_fader.calculate_user_volume(real_volume)
    expected_user_volume = real_volume / track_fader.fade_volume
    assert result == expected_user_volume
    assert is_same == False
    
def test_fade_out_on_play_no_fade_out_defined(track_fader, mocker):
    track_fader.logger = MagicMock()

    track_fader.stream.get_position = MagicMock(return_value=0.0)

    track_fader.stream.stop = MagicMock()

    track_fader.fade_out_start = None
    track_fader.fade_out_end = None

    track_fader.fade_out_on_play()

    track_fader.logger.debug.assert_called_once()
    track_fader.stream.stop.assert_called_once()

def test_fade_out_on_play_normal_state(track_fader, mocker):
    track_fader.logger = MagicMock()

    track_fader.stream.get_position = MagicMock(return_value=10.0)

    track_fader.state = FadeState.Normal

    track_fader.fade_out_start = 5.0
    track_fader.fade_out_end = 15.0

    track_fader.fade_out_on_play()

    track_fader.logger.debug.assert_called_once()
    
def test_get_user_volume(track_fader):
    track_fader.user_volume = 0.8
    track_fader.fade_volume = 0.5
    
    user_volume = track_fader.get_user_volume()
    
    assert user_volume == track_fader.user_volume

def test_get_user_volume_1(track_fader):
    track_fader.user_volume = 0
    track_fader.fade_volume = 0
    
    user_volume = track_fader.get_user_volume()
    
    assert user_volume == track_fader.user_volume
    
def test_get_user_volume_2(track_fader):
    track_fader.user_volume = 2
    track_fader.fade_volume = 2
    
    user_volume = track_fader.get_user_volume()
    
    assert user_volume == track_fader.user_volume

def test_get_user_volume_3(track_fader):
    track_fader.user_volume = -1
    track_fader.fade_volume = 10
    
    user_volume = track_fader.get_user_volume()
    
    assert user_volume == track_fader.user_volume

def test_get_user_volume_4(track_fader):
    track_fader.user_volume = 2
    track_fader.fade_volume = 1000
    
    user_volume = track_fader.get_user_volume()
    
    assert user_volume == track_fader.user_volume
    
def test_get_user_volume_5(track_fader):
    track_fader.user_volume = -1
    track_fader.fade_volume = -1
    
    user_volume = track_fader.get_user_volume()
    
    assert user_volume == track_fader.user_volume

def test_get_user_volume_5(track_fader):
    track_fader.user_volume = 10000
    track_fader.fade_volume = -1
    
    user_volume = track_fader.get_user_volume()
    
    assert user_volume == track_fader.user_volume

def test_is_fading_out_when_fading_out(track_fader):
    track_fader.state = FadeState.FadingOut
  
    result = track_fader.is_fading_out()

    assert result is True

def test_is_fading_out_when_not_fading_out(track_fader):
    track_fader.state = FadeState.Normal
    
    result = track_fader.is_fading_out()
    
    assert result is False

def test_setup_track_with_fade_in_and_fade_out(track_fader):
    # Mock the required methods and attributes
    track = MagicMock()
    track.get_tag_raw.side_effect = lambda tag: {
        '__startoffset': 0,
        '__stopoffset': 100
    }.get(tag, None)
    track.get_tag_raw.return_value = 100
    track_fader.calculate_fades = MagicMock()
    track_fader.play = MagicMock()
    track_fader.fade_out_end = "fade"
    
    # Call the method
    track_fader.setup_track(track, fade_in=5, fade_out=10)
    
    # Assert the calls made and the state of the TrackFader
    track_fader.play.assert_called_once()
    track_fader.calculate_fades.assert_called_once()
    assert track_fader.fade_out_start is None
    assert track_fader.fade_out_end is not None

def test_setup_track_without_fade(track_fader):
    # Mock the required methods and attributes
    track = MagicMock()
    track.get_tag_raw.side_effect = lambda tag: {
        '__startoffset': 0,
        '__stopoffset': 100
    }.get(tag, None)
    track.get_tag_raw.return_value = 0
    track_fader.calculate_fades = MagicMock()
    track_fader.play = MagicMock()
    track_fader.fade_out_end = "fade"

    track_fader.setup_track(track, fade_in=None, fade_out=None)

    track_fader.play.assert_called_once()
    track_fader.calculate_fades.assert_not_called()
    assert track_fader.fade_out_start is None
    assert track_fader.fade_out_end is not None
    
def test_setup_track_without_fade(track_fader):
    track = MagicMock()
    track.get_tag_raw.side_effect = lambda tag: {
        '__startoffset': 0,
        '__stopoffset': 100
    }.get(tag, None)
    track.get_tag_raw.return_value = 0
    track_fader.calculate_fades = MagicMock(return_value=("a", "b", "start", "end"))
    track_fader.play = MagicMock()
    track_fader.fade_out_end = "fade"
    
    track_fader.setup_track(track, fade_in=None, fade_out=None)
    
    track_fader.play.assert_called_once()
    track_fader.calculate_fades.assert_not_called()
    assert track_fader.fade_out_start is None
    assert track_fader.fade_out_end is not None
    
def test_play_with_fade_in(track_fader):
    track_fader._next = MagicMock()
    track_fader.play(fade_in_start=0, fade_in_end=5)
    
    track_fader._next.assert_called_once()
    assert track_fader.fade_in_start == 0
    assert track_fader.fade_in_end == 5
    assert track_fader.fade_out_start is None
    assert track_fader.fade_out_end is None
    assert track_fader.state == FadeState.FadingIn

def test_play_with_fade_out(track_fader):
    track_fader.play(fade_out_start=10, fade_out_end=15)
    
    assert track_fader.fade_in_start is None
    assert track_fader.fade_in_end is None
    assert track_fader.fade_out_start == 10
    assert track_fader.fade_out_end == 15
    assert track_fader.state == FadeState.Normal

def test_play_with_fade_out_1(track_fader):
    track_fader.play(fade_out_start=2, fade_out_end=3)
    
    assert track_fader.fade_out_start == 2
    assert track_fader.fade_out_end == 3
    assert track_fader.state == FadeState.Normal

def test_play_with_fade_out_2(track_fader):
    track_fader.play(fade_out_start=3, fade_out_end=4, fade_in_end=3)
    
    assert track_fader.fade_out_start == 3
    assert track_fader.fade_out_end == 4
    assert track_fader.fade_in_start is None
    assert track_fader.fade_in_end == 3
    assert track_fader.state == FadeState.Normal

def test_play_with_no_fade(track_fader):
    track_fader.play()
    
    assert track_fader.fade_in_start is None
    assert track_fader.fade_in_end is None
    assert track_fader.fade_out_start is None
    assert track_fader.fade_out_end is None
    assert track_fader.state == FadeState.NoFade
    
def test_pause(track_fader):
    track_fader._cancel = MagicMock()
    track_fader.pause()
    
    track_fader._cancel.assert_called_once()

def test_seek(track_fader):
    track_fader._next = MagicMock()
    
    track_fader.seek("to")
    
    track_fader._next.assert_called_once_with(now="to")

def test_set_user_volume(track_fader):
    volume = 0.5
    
    track_fader.set_user_volume(volume)

    assert track_fader.user_volume == volume
    track_fader.stream.set_volume.assert_called_once_with(volume * track_fader.fade_volume)

def test_set_user_volume_1(track_fader):
    volume = 1
    
    track_fader.set_user_volume(volume)

    assert track_fader.user_volume == volume
    track_fader.stream.set_volume.assert_called_once_with(volume * track_fader.fade_volume)
    
def test_set_user_volume_2(track_fader):
    volume = 2
    
    track_fader.set_user_volume(volume)

    assert track_fader.user_volume == volume
    track_fader.stream.set_volume.assert_called_once_with(volume * track_fader.fade_volume)

def test_set_user_volume_3(track_fader):
    volume = -1
    
    track_fader.set_user_volume(volume)

    assert track_fader.user_volume == volume
    track_fader.stream.set_volume.assert_called_once_with(volume * track_fader.fade_volume)
    
def test_set_user_volume_4(track_fader):
    volume = 0
    
    track_fader.set_user_volume(volume)

    assert track_fader.user_volume == volume
    track_fader.stream.set_volume.assert_called_once_with(volume * track_fader.fade_volume)

def test_set_user_volume_5(track_fader):
    volume = 10
    
    track_fader.set_user_volume(volume)

    assert track_fader.user_volume == volume
    track_fader.stream.set_volume.assert_called_once_with(volume * track_fader.fade_volume)

def test_set_fade_volume(track_fader):
    track_fader.set_fade_volume(0.5)

    assert track_fader.fade_volume == 0.5

    track_fader.stream.set_volume.assert_called_once_with(track_fader.user_volume * 0.5)

def test_set_fade_volume(track_fader):
    track_fader.set_fade_volume(0.5)

    assert track_fader.fade_volume == 0.5

    track_fader.stream.set_volume.assert_called_once_with(track_fader.user_volume * 0.5)

def test_set_fade_volume_1(track_fader):
    track_fader.set_fade_volume(1)

    assert track_fader.fade_volume == 1

    track_fader.stream.set_volume.assert_called_once_with(track_fader.user_volume * 1)
    
def test_set_fade_volume_2(track_fader):
    track_fader.set_fade_volume(2)

    assert track_fader.fade_volume == 2

    track_fader.stream.set_volume.assert_called_once_with(track_fader.user_volume * 2)

def test_set_fade_volume_3(track_fader):
    track_fader.set_fade_volume(0)

    assert track_fader.fade_volume == 0

    track_fader.stream.set_volume.assert_called_once_with(track_fader.user_volume * 0)
    
def test_set_fade_volume_4(track_fader):
    track_fader.set_fade_volume(-1)

    assert track_fader.fade_volume == -1

    track_fader.stream.set_volume.assert_called_once_with(track_fader.user_volume * (-1))

def test_unpause(track_fader): 
    track_fader._next = MagicMock()
    
    track_fader.unpause()
    
    track_fader._next.assert_called_once()
    
def test_stop(track_fader): 
    track_fader._cancel = MagicMock()
    
    track_fader.stop()
    
    track_fader._cancel.assert_called_once()
    
def test_next_with_fading_in(track_fader):
    track_fader._on_fade_start = MagicMock()
    track_fader.state = FadeState.FadingIn
    track_fader.fade_in_end = 2
    track_fader.fade_in_end = 15
    track_fader.fade_out_end = 1
    track_fader.fade_out_start=2
    track_fader._next(now=10)

    assert track_fader.state == FadeState.FadingIn

    track_fader._on_fade_start.assert_called_once_with(now=10)

def test_next_with_fade_out_start_none(track_fader):
    track_fader.set_fade_volume = MagicMock()
    track_fader.state = FadeState.Normal
    track_fader.fade_in_end = 15
    track_fader.fade_out_end = 1

    track_fader.fade_out_start = None

    track_fader._next()
    
    assert track_fader.state == FadeState.NoFade

    track_fader.set_fade_volume.assert_called_once_with(1.0)

def test_next_with_fade_out_start_not_none(track_fader):
    track_fader.set_fade_volume = MagicMock()
    track_fader._on_fade_start = MagicMock()
    track_fader.state = FadeState.Normal
    
    track_fader.fade_out_start = None
    track_fader.fade_in_end = 15
    track_fader.fade_out_end = 1

    track_fader.stream.get_position.return_value = 10

    track_fader._next()


    assert track_fader.state == FadeState.NoFade


    track_fader.set_fade_volume.assert_called_once_with(1.0)

    track_fader._on_fade_start.assernt_not_called()

def test_next_with_fade_out_start_not_none_1(track_fader):
    track_fader.set_fade_volume = MagicMock()
    track_fader._on_fade_start = MagicMock()
    track_fader.state = FadeState.Normal
    
    track_fader.fade_out_start = None
    track_fader.fade_in_end = 15
    track_fader.fade_out_end = 2

    track_fader.stream.get_position.return_value = 10

    track_fader._next()


    assert track_fader.state == FadeState.NoFade


    track_fader.set_fade_volume.assert_called_once_with(1.0)

    track_fader._on_fade_start.assernt_not_called()
    
def test_cancel(track_fader):
    track_fader.timer_id = 12345

    track_fader._cancel()

    assert track_fader.timer_id is None
    
def test_on_fade_start_fading_in(track_fader):
    track_fader._execute_fade = MagicMock(return_value=True)
    track_fader.fade_in_start = 0
    track_fader.fade_in_end = 10
    track_fader.state = FadeState.FadingIn

    result = track_fader._on_fade_start()
    track_fader._execute_fade.assert_called_once()
    assert track_fader.state == FadeState.FadingIn

def test_on_fade_start_fading_out(track_fader):
    track_fader._execute_fade = MagicMock(return_value=True)
    track_fader.on_fade_out = MagicMock()
    
    track_fader.fade_out_start = 0
    track_fader.fade_out_end = 10
    track_fader.state = FadeState.Normal

    result = track_fader._on_fade_start()
    track_fader._execute_fade.assert_called_once()
    track_fader.on_fade_out.assert_called()
    assert track_fader.state == FadeState.FadingOut

def test_on_fade_start_fading_out_already(track_fader):
    track_fader._execute_fade = MagicMock(return_value=True)
    track_fader.fade_out_start = 0
    track_fader.fade_out_end = 10
    track_fader.state = FadeState.FadingOut

    result = track_fader._on_fade_start()
    track_fader._execute_fade.assert_called_once()
    assert track_fader.state == FadeState.FadingOut
    
def test_execute_fade_fading_in(track_fader):
    track_fader.set_fade_volume = MagicMock()
    
    track_fader.state = FadeState.FadingIn
    track_fader.now = 0
    fade_start = 0
    fade_len = 10

    result = track_fader._execute_fade(fade_start, fade_len)

    track_fader.set_fade_volume.assert_called_once()
    
    assert result == True
    assert track_fader.fade_volume == pytest.approx(1.0)

def test_execute_fade_fading_out(track_fader):
    track_fader.set_fade_volume = MagicMock()
    
    track_fader.state = FadeState.FadingOut
    track_fader.now = 0
    fade_start = 0
    fade_len = 10

    result = track_fader._execute_fade(fade_start, fade_len)

    track_fader.set_fade_volume.assert_called_once()
    
    assert result == True

    assert track_fader.fade_volume == pytest.approx(1.0)  # Assuming 1 - (0.01 / 10)

def test_execute_fade_end_fading_in(track_fader):
    track_fader.set_fade_volume = MagicMock()
    track_fader._next = MagicMock()
    
    track_fader.state = FadeState.FadingIn
    track_fader.fade_in_end = 1
    track_fader.fade_out_end = 1
    track_fader.now = 10
    fade_start = 0
    fade_len = 10

    result = track_fader._execute_fade(fade_start, fade_len)

    track_fader.set_fade_volume.assert_called_once()
    track_fader._next.assert_called_once()
    
    assert result == False
    assert track_fader.state == FadeState.Normal

def test_execute_fade_end_fading_out_1(track_fader):
    track_fader.set_fade_volume = MagicMock()
    
    track_fader.state = FadeState.FadingOut
    track_fader.fade_in_end = 1
    track_fader.fade_out_end = 1
    track_fader.now = 10
    fade_start = 0
    fade_len = 10

    result = track_fader._execute_fade(fade_start, fade_len)

    track_fader.set_fade_volume.assert_called_once()
    
    assert result == False
    assert track_fader.state == FadeState.NoFade

def test_execute_fade_end_fading_out(track_fader):
    track_fader.state = FadeState.FadingOut
    track_fader.now = 10
    fade_start = 0
    fade_len = 10

    result = track_fader._execute_fade(fade_start, fade_len)

    assert result == False
    assert track_fader.timer_id == None
    assert track_fader.state == FadeState.NoFade