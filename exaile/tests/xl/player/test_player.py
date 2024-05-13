import time
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

def test_modify_volume_1(player):
    player.modify_volume(0)
    assert player.get_volume() == 50

def test_modify_volume_1(player):
    player.modify_volume(1)
    assert player.get_volume() == 51

def test_modify_volume_2(player):
    player.modify_volume(2)
    assert player.get_volume() == 53


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

def test_play_stop(player):
    player.stop = MagicMock()
    player.play(None)
    player.stop.assert_called_once()

def test_play_start_1(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=True)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 0, False, False,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 0, False, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_2(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=False)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 0, False, False,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 0, False, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_3(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=False)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 1, False, False,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 1, False, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_4(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=False)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 2, False, False,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 2, False, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_5(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=True)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 1, False, False,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 1, False, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_6(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=True)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 2, False, False,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 2, False, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_7(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=True)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 3, True, False,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 3, True, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_8(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=True)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 4, True, True,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, 4, True, True,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_play_start_9(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=True)
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, -1, False, True,))
    player.play(mock_track)
    player._engine.play.assert_called_once_with(mock_track, -1, False, True,)
    player._get_play_params.assert_called_once_with(mock_track, None, False, False, False)

def test_stop_when_playing(player):
    player.get_state = MagicMock(return_value='playing')
    player._engine.stop = MagicMock()
    result = player.stop()
    player._engine.stop.assert_called_once()
    assert result is True

def test_stop_when_paused(player):
    player.get_state = MagicMock(return_value='paused')
    player._engine.stop = MagicMock()

    result = player.stop()
    player._engine.stop.assert_called_once()
    assert result is True

def test_stop_when_not_playing_or_paused(player):
    player.get_state = MagicMock(return_value='stopped')
    player._engine.stop = MagicMock()
    result = player.stop()
    player._engine.stop.assert_not_called()
    assert result is False 

def test_play_start_paused(player):
    mock_track = MagicMock()
    player.is_stopped = MagicMock(return_value=True) 
    player._engine = MagicMock()
    player._get_play_params = MagicMock(return_value=(mock_track, 0, False, False,))
    player.play(mock_track, paused=True)
    player._engine.play.assert_called_once_with(mock_track, 0, False, False,)
    player._get_play_params.assert_called_once_with(mock_track, None, True, False, False)

def test_pause_when_playing(player):
    player.is_playing = MagicMock(return_value=True)
    player._update_playtime = MagicMock()
    player._reset_playtime_stamp = MagicMock()
    player._engine.pause = MagicMock()

    result = player.pause()
    
    player._update_playtime.assert_called_once()
    player._reset_playtime_stamp.assert_called_once()

    player._engine.pause.assert_called_once()
    
    assert result is True

def test_pause_when_not_playing(player):
    player.is_playing = MagicMock(return_value=False)
    player._engine.pause = MagicMock()
    
    result = player.pause()

    player._engine.pause.assert_not_called()

    assert result is False

def test_unpause_when_paused(player):
    player.is_paused = MagicMock(return_value=True)
    player._reset_playtime_stamp = MagicMock()
    player._engine.unpause = MagicMock()

    result = player.unpause()

    player._reset_playtime_stamp.assert_called_once()

    player._engine.unpause.assert_called_once()
    assert result is True

def test_unpause_when_not_paused(player):
    player.is_paused = MagicMock(return_value=False)
    player._engine.unpause = MagicMock()
    
    result = player.unpause()
    
    player._engine.unpause.assert_not_called()

    assert result is False

def test_toggle_pause_when_paused(player):
    player.get_state = MagicMock(return_value='paused')
    player.unpause = MagicMock(return_value=True)
    
    result = player.toggle_pause()

    player.unpause.assert_called_once()

    assert result is True

def test_toggle_pause_when_playing(player):
    player.get_state = MagicMock(return_value='playing')
    player.pause = MagicMock(return_value=True)
    result = player.toggle_pause()

    player.pause.assert_called_once()

    assert result is True

def test_toggle_pause_when_stopped(player):
    player.get_state = MagicMock(return_value='stopped')

    result = player.toggle_pause()

    assert result is False

def test_get_position(player):
    player._engine.get_position = MagicMock(return_value=2)

    position = player.get_position()

    player._engine.get_position.assert_called_once()

    assert position == 2

def test_get_position_1(player):
    player._engine.get_position = MagicMock(return_value=1)

    position = player.get_position()

    player._engine.get_position.assert_called_once()

    assert position == 1

def test_get_time(player):
    player.get_position = MagicMock(return_value=3000000000)


    time = player.get_time()

    player.get_position.assert_called_once()

    assert time == 3.0

def test_get_time_1(player):
    player.get_position = MagicMock(return_value=0000000000)


    time = player.get_time()

    player.get_position.assert_called_once()

    assert time == 0.0

def test_get_progress_with_duration_info(player):
    player.get_time = MagicMock(return_value=30.0)
    player._engine.get_current_track = MagicMock()
    player._engine.get_current_track.return_value.get_tag_raw.return_value = 60.0

    progress = player.get_progress()

    player.get_time.assert_called_once()
    player._engine.get_current_track.return_value.get_tag_raw.assert_called_once_with("__length")
    
    assert progress == 0.5

def test_get_progress_without_duration_info(player):
    player.get_time = MagicMock(return_value=30.0)
    player._engine.get_current_track = MagicMock()
    player._engine.get_current_track.return_value.get_tag_raw.side_effect = TypeError

    progress = player.get_progress()

    player.get_time.assert_called_once()
    player._engine.get_current_track.return_value.get_tag_raw.assert_called_once_with("__length")

    assert progress == 0.0

def test_get_progress_no_current_track(player):
    player._engine.get_current_track = MagicMock(return_value=None)
    progress = player.get_progress()

    assert progress == 0.0

def test_set_progress_with_current_track(player):
    player._engine.get_current_track = MagicMock()
    player.current.get_tag_raw = MagicMock(return_value=2)
    player.seek = MagicMock()

    player.set_progress(0.5)

    player.current.get_tag_raw.assert_called_once_with('__length')
    player.seek.assert_called_once_with(0.5 * 2)

def test_set_progress_with_current_track_1(player):
    player._engine.get_current_track = MagicMock()
    player.current.get_tag_raw = MagicMock(return_value=3)
    player.seek = MagicMock()

    player.set_progress(1)

    player.current.get_tag_raw.assert_called_once_with('__length')
    player.seek.assert_called_once_with(0.5 * 3)

def test_set_progress_with_current_track_1(player):
    player._engine.get_current_track = MagicMock()
    player.current.get_tag_raw = MagicMock(return_value=0)
    player.seek = MagicMock()

    player.set_progress(1)

    player.current.get_tag_raw.assert_called_once_with('__length')
    player.seek.assert_called_once_with(1 * 0)

def test_set_progress_without_current_track(player):
    player._engine.get_current_track = None
    player.seek = MagicMock()

    player.set_progress(0.5)
    player.seek.assert_called_once()

def test_set_progress_with_attribute_error(player):
    player._engine.get_current_track = MagicMock()
    player.current.get_tag_raw.side_effect = AttributeError
    player.seek = MagicMock()

    player.set_progress(0.5)

    player.seek.assert_called_once()

def test_set_progress_with_type_error(player):
    player._engine.get_current_track = MagicMock()
    player.current.get_tag_raw.side_effect = TypeError
    player.seek = MagicMock()

    player.set_progress(0.5)

    player.seek.assert_called_once()

# def test_set_progress_without_current_track(player):
#     player._engine.get_current_track = None
#     player.current.get_tag_raw = MagicMock(return_value='')
#     player.seek = MagicMock()

#     player.set_progress(0.5)

#     player.seek.assert_not_called()

def test_modify_time_with_current_track(player):
    player._engine.get_current_track = MagicMock()
    player.get_time = MagicMock(return_value=30.0)
    player.current.get_tag_raw = MagicMock(return_value=60.0)
    player.seek = MagicMock()

    player.modify_time(10)

    player.get_time.assert_called_once()
    player.current.get_tag_raw.assert_called_once_with('__length')

    player.seek.assert_called_once_with(40)

def test_modify_time_without_current_track(player):
    player._engine.get_current_track = None
    player.get_time = MagicMock()

    player.seek = MagicMock()

    player.modify_time(10)

    player.get_time.assert_not_called()
    player.seek.assert_not_called()

def test_modify_time_with_no_length_info(player):
    player._engine.get_current_track = MagicMock()
    player.get_time = MagicMock()
    player.current.get_tag_raw = MagicMock(side_effect=TypeError)
    player.seek = MagicMock()

    player.modify_time(10)

    player.seek.assert_not_called()

def test_modify_time_with_no_length_info_1(player):
    player._engine.get_current_track = MagicMock()
    player.get_time = MagicMock()
    player.current.get_tag_raw = MagicMock(side_effect=AttributeError)
    player.seek = MagicMock()

    player.modify_time(10)

    player.seek.assert_not_called()

def test_modify_time_seek_outside_track_bounds(player):
    player._engine.get_current_track = MagicMock()
    player.get_time = MagicMock(return_value=55.0) 
    player.current.get_tag_raw = MagicMock(return_value=60.0) 
    player.seek = MagicMock()
    
    player.modify_time(10)

    player.seek.assert_called_once_with(58)

def test_get_state_playing(player):
    player._engine.get_state = MagicMock(return_value='playing')
    
    state = player.get_state()

    player._engine.get_state.assert_called_once()
    assert state == 'playing'

def test_get_state_paused(player):
    player._engine.get_state = MagicMock(return_value='paused')

    state = player.get_state()

    player._engine.get_state.assert_called_once()
    assert state == 'paused'

def test_get_state_stopped(player):
    player._engine.get_state = MagicMock(return_value='stopped')
    state = player.get_state()

    player._engine.get_state.assert_called_once()

    assert state == 'stopped'

def test_is_playing_when_playing(player):
    player._engine.get_state = MagicMock(return_value='playing')

    is_playing = player.is_playing()

    player._engine.get_state.assert_called_once()

    assert is_playing is True

def test_is_playing_when_paused(player):
    player._engine.get_state = MagicMock(return_value='paused')

    is_playing = player.is_playing()
    player._engine.get_state.assert_called_once()
    assert is_playing is False

def test_is_playing_when_stopped(player):
    player._engine.get_state = MagicMock(return_value='stopped')

    is_playing = player.is_playing()

    player._engine.get_state.assert_called_once()

    assert is_playing is False

def test_is_paused_when_stopped(player):
    player._engine.get_state = MagicMock(return_value='stopped')

    is_paused = player.is_paused()

    player._engine.get_state.assert_called_once()

    assert is_paused is False

def test_is_paused_when_playing(player):
    player._engine.get_state = MagicMock(return_value='playing')

    is_paused = player.is_paused()

    player._engine.get_state.assert_called_once()

    assert is_paused is False

def test_is_paused_when_paused(player):
    player._engine.get_state = MagicMock(return_value='paused')

    is_paused = player.is_paused()

    player._engine.get_state.assert_called_once()

    assert is_paused is True

def test_is_stopped_when_stopped(player):
    player._engine.get_state = MagicMock(return_value='stopped')

    is_stopped = player.is_stopped()

    player._engine.get_state.assert_called_once()

    assert is_stopped is True

def test_is_stopped_when_playing(player):
    player._engine.get_state = MagicMock(return_value='playing')

    is_stopped = player.is_stopped()

    player._engine.get_state.assert_called_once()

    assert is_stopped is False

def test_is_stopped_when_paused(player):
    player._engine.get_state = MagicMock(return_value='paused')

    is_paused = player.is_stopped()

    player._engine.get_state.assert_called_once()

    assert is_paused is False

def test_engine_load_volume(player):
    player._volume = 0.5
    player._engine.set_volume = MagicMock()
    player.engine_load_volume()

    player._engine.set_volume.assert_called_once_with(0.5)

def test_engine_notify_track_start(player):
    player._reset_playtime_stamp = MagicMock()

    track = MagicMock()
    player.engine_notify_track_start(track)

    player._reset_playtime_stamp.assert_called_once()

def test_engine_notify_track_end_not_done(player):
    player._update_playtime = MagicMock()
    player._cancel_delayed_start = MagicMock()

    track = MagicMock()
    done = False

    player.engine_notify_track_end(track, done)

    player._update_playtime.assert_called_once_with(track)

    player._cancel_delayed_start.assert_not_called()

def test_engine_autoadvance_get_next_track_auto_advance_disabled(player):
    player._auto_advance = False
    player.queue = MagicMock()

    next_track = player.engine_autoadvance_get_next_track()

    player.queue.get_next.assert_not_called()

    assert next_track is None

def test_engine_autoadvance_get_next_track_auto_advance_enabled_gapless_disabled(player):
    player._auto_advance = True
    player._auto_advance_delay = 0
    player._gapless_enabled = False
    player.queue = MagicMock()

    next_track = player.engine_autoadvance_get_next_track()

    player.queue.get_next.assert_called_once()

    
    assert next_track == player.queue.get_next.return_value

def test_engine_autoadvance_get_next_track_auto_advance_enabled_gapless_enabled(player):
    player._auto_advance = True
    player._auto_advance_delay = 0
    player._gapless_enabled = True
    player.queue = MagicMock()

    next_track = player.engine_autoadvance_get_next_track(gapless=True)

    player.queue.get_next.assert_called_once()

    
    assert next_track == player.queue.get_next.return_value

def test_engine_autoadvance_get_next_track_auto_advance_enabled_gapless_disabled_delay_nonzero(player):
    player._auto_advance = True
    player._auto_advance_delay = 1
    player._gapless_enabled = False
    player.queue = MagicMock()

    next_track = player.engine_autoadvance_get_next_track()

    player.queue.get_next.assert_called_once()

    assert next_track is not None

def test_engine_autoadvance_get_next_track_auto_advance_enabled_gapless_enabled_delay_nonzero(player):
    player._auto_advance = True
    player._auto_advance_delay = 1
    player._gapless_enabled = False
    player.queue = MagicMock()

    next_track = player.engine_autoadvance_get_next_track(True)

    player.queue.get_next.assert_not_called()

    assert next_track is None

def test_engine_autoadvance_notify_next_with_next_track(player):
    player.queue = MagicMock()
    player.queue.next = MagicMock(return_value="next_track")
    player._get_play_params = MagicMock(return_value=("next_track", None, False, False, True))


    result = player.engine_autoadvance_notify_next("buffered_track")

    player.queue.next.assert_called_once_with(autoplay=False)

    player._get_play_params.assert_called_once_with("buffered_track", None, False, False, True)
    assert result == ("next_track", None, False, False, True)

def test_engine_autoadvance_notify_next_without_next_track(player):
    player.queue = MagicMock()
    player.queue.next = MagicMock(return_value=None)
    player._get_play_params = MagicMock(return_value=("buffered_track", None, False, False, True))

    result = player.engine_autoadvance_notify_next("buffered_track")

    player.queue.next.assert_called_once_with(autoplay=False)

    player._get_play_params.assert_called_once_with("buffered_track", None, False, True, True)

    assert result == ("buffered_track", None, False, False, True)

def test_get_play_params_start_at_none(player):
    track = MagicMock()
    track.get_tag_raw.return_value = None
    player._cancel_delayed_start = MagicMock()

    result = player._get_play_params(track, None, False, False, True)

    player._cancel_delayed_start.assert_called_once()

    assert result == (track, None, False, False)

def test_get_play_params_start_at_positive_offset(player):
    player._cancel_delayed_start = MagicMock()

    track = MagicMock()
    
    result = player._get_play_params(track, 10, False, False, True)

    player._cancel_delayed_start.assert_called_once()
    assert result == (track, 10, False, False)

def test_get_play_params_paused_autoadvance_delay_positive(player):
    player._cancel_delayed_start = MagicMock()
    player._delayed_start = MagicMock()
    player._auto_advance_delay = 100
    player._delay_id = None

    track = MagicMock()
    result = player._get_play_params(track, 10, False, False, True)

    player._cancel_delayed_start.assert_called_once()

    assert player._delay_id is not None  
    assert result == (track, 10, True, False)

def test_get_play_params_paused_autoadvance_delay_zero(player):
    player._cancel_delayed_start = MagicMock()
    player._auto_advance_delay = 0

    track = MagicMock()
    result = player._get_play_params(track, 10, False, False, True)

    player._cancel_delayed_start.assert_called_once()

    assert result == (track, 10, False, False)

def test_get_play_params_not_paused_autoadvance_false(player):
    player._cancel_delayed_start = MagicMock()
    
    track = MagicMock()
    result = player._get_play_params(track, 10, True, False, False)

    player._cancel_delayed_start.assert_called_once()

    assert result == (track, 10, True, False)

def test_delayed_start(player):
    player.unpause = MagicMock()

    player._delayed_start()

    player.unpause.assert_called_once()

def test_update_playtime_with_track_and_playtime_stamp(player):
    track = MagicMock()
    track.get_tag_raw.return_value = "10"
    player._playtime_stamp = 10

    player._update_playtime(track)

    track.get_tag_raw.assert_called_once_with('__playtime')
    track.set_tag_raw.assert_called_once_with(
                '__playtime', 10 + int(time.time() - 10)
    )
    
    assert player._playtime_stamp is None

def test_update_playtime_with_track_and_no_playtime_stamp(player):

    track = MagicMock()
    track.get_tag_raw.return_value = "10" 
    player._playtime_stamp = 10

    player._update_playtime(track)

    track.get_tag_raw.assert_called_once_with('__playtime')

    track.set_tag_raw.assert_called_once()

    assert player._playtime_stamp is None

def test_update_playtime_with_no_track(player):
    player._update_playtime(None)

    assert player._playtime_stamp is None
    
def test_get_play_params_no_start_at(player):
    mock_track = MagicMock()
    mock_track.get_tag_raw.return_value = None
    params = player._get_play_params(mock_track, None, False, False, False)
    assert params == (mock_track, None, False, False)

def test_get_play_params_start_at_from_track(player):
    mock_track = MagicMock()
    mock_track.get_tag_raw.return_value = 10
    params = player._get_play_params(mock_track, None, False, False, False)
    assert params == (mock_track, 10, False, False)

def test_get_play_params_paused_autoadvance(player):
    mock_track = MagicMock()
    mock_track.get_tag_raw.return_value = None
    
    player._auto_advance_delay = 1000
    params = player._get_play_params(mock_track, None, False, False, True)
    assert params == (mock_track, None, True, False)
    
