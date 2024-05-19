
from unittest.mock import MagicMock

from xl.player.gst.engine import ExaileGstEngine


def test_exaile_gst_engine_initialization():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    assert engine.name == "TestEngine"
    assert engine.player == player_mock
    assert engine.logger is not None
    assert engine.crossfade_duration == 3000
    assert engine.audiosink_device is None
    assert engine.audiosink is None
    assert engine.custom_sink_pipe is None
    assert engine.disable_autoswitch is True
    assert engine.user_fade_enabled is False
    assert engine.user_fade_duration == 1000

def test_exaile_gst_engine_settings_options():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.settings_unsubscribe.unsubscribe = MagicMock()

    assert engine.audiosink_device == None
    assert engine.settings_unsubscribe.unsubscribe.call_count == 0

def test_exaile_gst_engine_methods():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)

    engine._apply_audio_plugins = MagicMock()
    engine._stop_playback = MagicMock()
    engine._start_playback = MagicMock()
    engine._apply_audio_plugins.assert_not_called()
    engine._stop_playback.assert_not_called()
    engine._start_playback.assert_not_called()
    
def test_setattr_initialized_false():
  player_mock = MagicMock()
  engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
  engine._reconfigure_crossfader = MagicMock()
  engine._reconfigure_sink = MagicMock()
  engine.initialized = False
  engine.__setattr__('crossfade_enabled', True)
  engine._reconfigure_crossfader.assert_not_called()
  engine._reconfigure_sink.assert_not_called()

def test_setattr_crossfade_enabled():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine._reconfigure_crossfader = MagicMock()
    engine._reconfigure_sink = MagicMock()
    engine.initialized = True
    engine.__setattr__('crossfade_enabled', True)
    engine._reconfigure_crossfader.assert_called_once()
    engine._reconfigure_sink.assert_not_called()

def test_setattr_crossfade_duration():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine._reconfigure_crossfader = MagicMock()
    engine._reconfigure_sink = MagicMock()
    engine.initialized = True
    engine.__setattr__('crossfade_duration', 5000)
    engine._reconfigure_crossfader.assert_called_once()
    engine._reconfigure_sink.assert_not_called()

def test_setattr_audiosink_device():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine._reconfigure_crossfader = MagicMock()
    engine._reconfigure_sink = MagicMock()
    engine.initialized = True
    engine.__setattr__('audiosink_device', 'device_name')
    engine._reconfigure_crossfader.assert_not_called()
    engine._reconfigure_sink.assert_called_once()

def test_setattr_custom_sink_pipe():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine._reconfigure_crossfader = MagicMock()
    engine._reconfigure_sink = MagicMock()
    engine.initialized = True
    engine.__setattr__('custom_sink_pipe', 'custom_pipe')
    engine._reconfigure_crossfader.assert_not_called()
    engine._reconfigure_sink.assert_called_once()

def test_initialize():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine._reconfigure_crossfader = MagicMock()

    engine.initialize()

    assert engine.initialized is True
    assert engine.main_stream is not None
    assert engine.other_stream is None
    assert engine.crossfade_out is None
    player_mock.engine_load_volume.assert_called_once()
    engine._reconfigure_crossfader.assert_called_once()
    
def test_reconfigure_crossfader_enabled():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.logger = MagicMock()
    engine.crossfade_enabled = True
    engine.crossfade_duration = 3000
    engine.other_stream = None
    engine.main_stream = MagicMock()
    engine.main_stream.get_user_volume = MagicMock(return_value=0.5)
    engine.main_stream.reconfigure_fader = MagicMock()
    
    engine._reconfigure_crossfader()

    assert engine.logger.info.call_count == 2
    assert engine.main_stream.reconfigure_fader.call_count == 1
    assert engine.other_stream is not None

def test_reconfigure_crossfader_disabled():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.logger = MagicMock()
    engine.crossfade_enabled = False
    engine.other_stream = MagicMock()
    engine.main_stream = MagicMock()
    engine.main_stream.reconfigure_fader = MagicMock()
    
    engine._reconfigure_crossfader()

    assert engine.logger.info.call_count == 2
    engine.main_stream.reconfigure_fader.assert_called_once_with(None, None)
    engine.other_stream.destroy.assert_called_once()

def test_reconfigure_sink():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.logger = MagicMock()
    engine.other_stream = MagicMock()
    engine.main_stream = MagicMock()

    engine._reconfigure_sink()

    engine.logger.info.assert_called_once_with("Reconfiguring audiosinks")
    engine.main_stream.reconfigure_sink.assert_called_once()
    engine.other_stream.reconfigure_sink.assert_called_once()

def test_reconfigure_sink_no_other_stream():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.logger = MagicMock()
    engine.other_stream = None
    engine.main_stream = MagicMock()

    engine._reconfigure_sink()

    engine.logger.info.assert_called_once_with("Reconfiguring audiosinks")
    engine.main_stream.reconfigure_sink.assert_called_once()
    
def test_destroy_permanent_true():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()
    engine.other_stream = MagicMock()
    engine.settings_unsubscribe = MagicMock()

    engine.destroy()

    engine.main_stream.destroy.assert_called_once()
    engine.other_stream.destroy.assert_called_once()
    engine.settings_unsubscribe.assert_called_once()
    assert engine.initialized is False
    assert engine.needs_sink is True
    assert engine.audiosink is None
    assert engine.audiosink_device is None

def test_destroy_permanent_false():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()
    engine.other_stream = MagicMock()
    engine.settings_unsubscribe = MagicMock()

    engine.destroy(permanent=False)

    engine.main_stream.destroy.assert_called_once()
    engine.other_stream.destroy.assert_called_once()
    engine.settings_unsubscribe.assert_not_called()
    assert engine.initialized is False
    assert engine.needs_sink is True
    assert engine.audiosink is None
    assert engine.audiosink_device is None

def test_destroy_no_other_stream():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()
    engine.other_stream = None
    engine.settings_unsubscribe = MagicMock()

    engine.destroy()

    engine.main_stream.destroy.assert_called_once()
    assert engine.settings_unsubscribe.call_count == 1
    assert engine.initialized is False
    assert engine.needs_sink is True
    assert engine.audiosink is None
    assert engine.audiosink_device is None
    

def test_get_current_track():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()
    expected_track = MagicMock()
    engine.main_stream.current_track = expected_track

    result = engine.get_current_track()

    assert result == expected_track

def test_get_position():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()

    expected_position = 10.0
    engine.main_stream.get_position.return_value = expected_position

    result = engine.get_position()

    assert result == expected_position
    engine.main_stream.get_position.assert_called_once()
    
def test_get_state_playing():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()
    engine.main_stream.get_gst_state.return_value = "PLAYING"

    result = engine.get_state()

    assert result == "stopped"
    engine.main_stream.get_gst_state.assert_called_once()

def test_get_state_paused():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()
    engine.main_stream.get_gst_state.return_value = "PAUSED"

    result = engine.get_state()

    assert result == "stopped"
    engine.main_stream.get_gst_state.assert_called_once()

def test_get_state_stopped():
    player_mock = MagicMock()
    engine = ExaileGstEngine("TestEngine", player_mock, disable_autoswitch=True)
    engine.main_stream = MagicMock()
    engine.main_stream.get_gst_state.return_value = "STOPPED"

    result = engine.get_state()

    assert result == "stopped"
    engine.main_stream.get_gst_state.assert_called_once()