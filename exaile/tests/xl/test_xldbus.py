import pytest
import dbus
import dbus.service
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gio
from collections import namedtuple
import logging
import sys
import xl.xldbus
from unittest.mock import patch, MagicMock, Mock, PropertyMock, call
from xl.xldbus import check_dbus, check_exit, run_commands, PlaybackStatus, DbusManager
from xl import player, trax, playlist, covers, event
from xl.nls import gettext as _
from xl.formatter import LengthTagFormatter
from xlgui import get_controller


mock_iface = MagicMock()

@pytest.fixture(autouse=True)
def mock_dbus():
    with patch('dbus.SessionBus') as mock_session:
        mock_session.return_value = MagicMock()
        with patch('dbus.service.BusName'):
            with patch('dbus.service.Object.__init__', return_value=None):
                yield

def test_check_dbus_available():
    bus = MagicMock()
    obj = MagicMock()
    dbus_iface = MagicMock()
    dbus_iface.ListNames.return_value = ['org.freedesktop.DBus', 'org.exaile.Exaile']
    obj.return_value = dbus_iface
    bus.get_object.return_value = obj
    with patch('dbus.Interface', return_value=dbus_iface):
        assert check_dbus(bus, 'org.exaile.Exaile') == True

def test_check_dbus_not_available():
    bus = MagicMock()
    dbus_iface = MagicMock()
    dbus_iface.ListNames.return_value = ['org.freedesktop.DBus']
    bus.get_object.return_value = dbus_iface
    assert check_dbus(bus, 'org.exaile.Exaile') == False

def test_check_dbus_returns_false():
    with patch('dbus.SessionBus') as mock_session_bus:
        mock_session_bus.return_value.get_object.side_effect = dbus.exceptions.DBusException("Not found")
        assert check_dbus(mock_session_bus, 'org.exaile.Exaile') == False

def test_check_exit_new_instance():
    options = MagicMock(NewInstance=True)
    args = MagicMock()
    with patch('dbus.SessionBus') as mock_session_bus:
        mock_session_bus.return_value.get_object.side_effect = dbus.exceptions.DBusException("Not found")
        assert check_exit(options, args) == "command"


def test_check_exit_dbus_command():
    options = MagicMock(NewInstance=False)
    setattr(options, 'GetArtist', True)
    args = []
    bus = MagicMock()
    iface = MagicMock()
    with patch('xl.xldbus.dbus.SessionBus', return_value=bus), \
         patch('xl.xldbus.check_dbus', return_value=True), \
         patch('xl.xldbus.dbus.Interface', return_value=iface):
        bus.get_object.return_value = iface
        iface.TestService = MagicMock()
        iface.Enqueue = MagicMock()
        result = check_exit(options, args)
        assert result == "exit"

def test_check_exit_currentInstance():
    options = MagicMock(NewInstance=False)
    args = MagicMock()
    with patch('dbus.SessionBus') as mock_session_bus:
        mock_session_bus.return_value.get_object.return_value = mock_iface
        assert check_exit(options, args) == "command"

def test_run_commands():
    options = MagicMock()
    with patch('dbus.SessionBus') as mock_session_bus:
        mock_session_bus.return_value.get_object.return_value = mock_iface
        run_commands(options, mock_iface)

def test_run_commands_notTriggered():
    options = MagicMock()
    setattr(options, 'Play', False)
    iface = MagicMock()
    run_commands(options, iface)
    iface.Play.assert_not_called()

def test_run_commands_triggered():
    options = MagicMock()
    setattr(options, 'Play', True)
    iface = MagicMock()
    run_commands(options, iface)
    iface.Play.assert_called_once()


def test_TestService_logger():
    mock_logger = MagicMock()
    with patch('xl.xldbus.logger', mock_logger):
        dbus_manager = DbusManager(MagicMock())
        test_arg = "test argument"
        dbus_manager.TestService(test_arg)
        mock_logger.debug.assert_called_with(test_arg)

def test_IsPlaying_playerStopped():
    player_mock = MagicMock()
    player_mock.is_stopped.return_value = True
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.IsPlaying() == False

def test_IsPlaying_playerPlaying():
    player_mock = MagicMock()
    player_mock.is_stopped.return_value = False
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.IsPlaying() == True

def test_GetTrackAttr_returns_value():
    player_mock = MagicMock()
    player_mock.current.get_tag_raw.return_value = "some_value"
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.GetTrackAttr("title") == "some_value"

def test_GetTrackAttr_returns_emptyString():
    player_mock = MagicMock()
    player_mock.current.get_tag_raw.side_effect = AttributeError("Error")
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.GetTrackAttr("title") == ""


def test_SetTrackAttr_setValue():
    player_mock = MagicMock()
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.SetTrackAttr("genre", "rock")
        player_mock.current.set_tag_raw.assert_called_with("genre", "rock")

def test_SetTrackAttr_exception():
    player_mock = MagicMock()
    player_mock.current.set_tag_raw.side_effect = AttributeError()
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.SetTrackAttr("genre", "rock")

def test_GetRating_correctValue():
    with patch('xl.xldbus.DbusManager.GetTrackAttr', return_value='4'):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.GetRating() == 4

def test_SetRating_setValue():
    with patch('xl.xldbus.DbusManager.SetTrackAttr') as mock_set_attr:
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.SetRating(5)
        mock_set_attr.assert_called_with('__rating', 5)

def test_ChangeVolume_increase():
    player_mock = MagicMock()
    initial_volume = 50
    change_amount = 10
    player_mock.get_volume.return_value = initial_volume
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.ChangeVolume(change_amount)
        player_mock.set_volume.assert_called_once_with(initial_volume + change_amount)

def test_ChangeVolume_decrease():
    player_mock = MagicMock()
    initial_volume = 50
    change_amount = -10
    player_mock.get_volume.return_value = initial_volume
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.ChangeVolume(change_amount)
        player_mock.set_volume.assert_called_once_with(initial_volume + change_amount)

def test_ToggleMute_mute():
    player_mock = MagicMock()
    player_mock.get_volume.return_value = 70
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.ToggleMute()
        player_mock.set_volume.assert_called_with(0)

def test_ToggleMute_unmute():
    player_mock = MagicMock()
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.cached_volume = 70
        dbus_manager.ToggleMute()
        player_mock.set_volume.assert_called_with(70)

def test_Seek_position():
    player_mock = MagicMock()
    seek_value = 120
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.Seek(seek_value)
        player_mock.seek.assert_called_once_with(seek_value)

def test_Prev():
    player_mock = MagicMock()
    with patch('xl.player.QUEUE', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.Prev()
        player_mock.prev.assert_called_once()

def test_Stop():
    player_mock = MagicMock()
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.Stop()
        player_mock.stop.assert_called_once()

def test_Next():
    player_mock = MagicMock()
    with patch('xl.player.QUEUE', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.Next()
        player_mock.next.assert_called_once()

def test_Play():
    player_mock = MagicMock()
    with patch('xl.player.QUEUE', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.Play()
        player_mock.play.assert_called_once()

def test_Pause():
    player_mock = MagicMock()
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.Pause()
        player_mock.pause.assert_called_once()

def test_PlayPause():
    player_mock = MagicMock()
    player_mock.is_stopped.return_value = True
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.PlayPause()
        player_mock.play.assert_called_once()

    player_mock.is_stopped.return_value = False
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager.PlayPause()
        player_mock.toggle_pause.assert_called_once()

def test_StopAfterCurrent():
    player_mock = MagicMock()
    with patch('xl.player.QUEUE', player_mock):
        dbus_manager = DbusManager(MagicMock())
        dbus_manager.StopAfterCurrent()
        assert player_mock.stop_track == player_mock.get_current()

def test_CurrentProgress_positive():
    player_mock = MagicMock()
    player_mock.get_progress.return_value = 0.5
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.CurrentProgress() == '50'

def test_CurrentProgress_negative():
    player_mock = MagicMock()
    player_mock.get_progress.return_value = -1
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.CurrentProgress() == ""

def test_CurrentPosition():
    player_mock = MagicMock()
    player_mock.get_time.return_value = 125
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.CurrentPosition() == '2:05'

def test_GetVolume():
    player_mock = MagicMock()
    player_mock.get_volume.return_value = 75
    with patch('xl.player.PLAYER', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.GetVolume() == '75'

def test_Query_not_playing():
    dbus_manager = DbusManager(MagicMock())
    status = PlaybackStatus(state='stopped', current=None, progress=0, position=0)
    with patch.object(dbus_manager, '_DbusManager__get_playback_status', return_value=status) as mock_status:
        assert dbus_manager.Query() == _('Not playing.')

def test_Query_correctInfo():
    dbus_manager = DbusManager(MagicMock())
    status = PlaybackStatus(
        state='playing',
        current={'title': 'Some Song', 'artist': 'Some Artist', 'album': 'Some Album', '__length': '3:30'},
        progress='10',
        position='0:30'
    )
    with patch.object(dbus_manager, '_DbusManager__get_playback_status', return_value=status) as mock_status:
        result = dbus_manager.Query()
        assert result == _('status: playing, title: Some Song, artist: Some Artist, album: Some Album, length: 3:30, position: 10% [0:30]')

def test_PlayFile():
    gui_mock = MagicMock()
    exaile_mock = MagicMock(gui=gui_mock)
    dbus_manager = DbusManager(exaile_mock)
    filename = "file:///music/song.mp3"
    dbus_manager.PlayFile(filename)
    gui_mock.open_uri.assert_called_once_with(filename)

def test_Enqueue():
    gui_controller_mock = MagicMock()
    with patch('xl.player.PLAYER.is_stopped', return_value=False), \
         patch('xlgui.get_controller', return_value=gui_controller_mock):
        dbus_manager = DbusManager(MagicMock())
        locations = ['file:///music/song1.mp3', 'file:///music/song2.mp3']
        dbus_manager.Enqueue(locations)
        assert gui_controller_mock.open_uri.call_count == len(locations)

def test_Add():
    trax_mock = MagicMock()
    tracks = ['track1', 'track2']
    collection_mock = MagicMock()
    exaile_mock = MagicMock(collection=collection_mock)
    with patch('xl.trax.get_tracks_from_uri', return_value=tracks) as mock_get_tracks:
        dbus_manager = DbusManager(exaile_mock)
        location = "file:///music/album"
        dbus_manager.Add(location)
        collection_mock.add_tracks.assert_called_once_with(tracks)

def test_ExportPlaylist():
    playlist_mock = MagicMock()
    queue_mock = MagicMock(current_playlist=playlist_mock)
    with patch('xl.player.QUEUE', queue_mock), \
         patch('xl.playlist.export_playlist') as export_mock:
        dbus_manager = DbusManager(MagicMock())
        location = "/test/export.m3u"
        dbus_manager.ExportPlaylist(location)
        export_mock.assert_called_once_with(playlist_mock, location)

def test_GuiToggleVisible():
    gui_mock = MagicMock()
    exaile_mock = MagicMock(gui=gui_mock)
    dbus_manager = DbusManager(exaile_mock)
    dbus_manager.GuiToggleVisible()
    gui_mock.main.toggle_visible.assert_called_once_with(bringtofront=True)

def test_get_playback_status_stopped():
    player_mock = MagicMock()
    player_mock.QUEUE.get_current.return_value = None
    player_mock.PLAYER.is_stopped.return_value = True
    dbus_manager = DbusManager(MagicMock())
    with patch('xl.player', player_mock):
        status = dbus_manager._DbusManager__get_playback_status()
        assert status.state == 'stopped' and status.current is None

def test_get_playback_status_playing():
    player_mock = MagicMock()
    player_mock.QUEUE.get_current.return_value = MagicMock()
    player_mock.PLAYER.is_stopped.return_value = False
    dbus_manager = DbusManager(MagicMock())
    expected_current = {'title': 'Test', '__length': '3:30', 'artist': 'Artist', 'album': 'Album'}
    with patch('xl.player', player_mock), \
         patch.object(dbus_manager, 'GetTrackAttr', side_effect=lambda tag: expected_current[tag]), \
         patch.object(dbus_manager, 'CurrentProgress', return_value='50'), \
         patch.object(dbus_manager, 'CurrentPosition', return_value='1:30'), \
         patch('xl.formatter.LengthTagFormatter.format_value', return_value='3:30'):
        status = dbus_manager._DbusManager__get_playback_status()
        assert status.current == expected_current and status.progress == '50'

def test_FormatQuery():
    dbus_manager = DbusManager(MagicMock())
    status_mock = MagicMock()
    status_mock._asdict.return_value = {'state': 'playing'}
    with patch.object(dbus_manager, '_DbusManager__get_playback_status', return_value=status_mock):
        result = dbus_manager.FormatQuery('json', 'title,artist')
        assert 'playing' in result

def test_FormatQuery_empty():
    dbus_manager = DbusManager(MagicMock())
    result = dbus_manager.FormatQuery('xml', 'title,artist')
    assert result == ''

def test_GetVersion():
    exaile_mock = MagicMock()
    exaile_mock.get_version.return_value = "1.0"
    dbus_manager = DbusManager(exaile_mock)
    assert dbus_manager.GetVersion() == "1.0"

def test_GetCoverData_no_cover():
    player_mock = MagicMock()
    covers_mock = MagicMock()
    covers_mock.MANAGER.get_cover.return_value = None
    with patch('xl.player', player_mock), patch('xl.covers', covers_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.GetCoverData() == ''

def test_GetCoverData_cover():
    player_mock = MagicMock()
    covers_mock = MagicMock()
    covers_mock.MANAGER.get_cover.return_value = 'cover data'
    with patch('xl.player', player_mock), patch('xl.covers', covers_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.GetCoverData() == 'cover data'

def test_GetState():
    player_mock = MagicMock()
    player_mock.PLAYER.get_state.return_value = 'playing'    
    with patch('xl.player', player_mock):
        dbus_manager = DbusManager(MagicMock())
        assert dbus_manager.GetState() == 'playing'

def test_StateChanged():
    dbus_manager = DbusManager(MagicMock())
    with patch.object(dbus_manager, 'StateChanged', return_value=None) as mock_method:
        dbus_manager.StateChanged()
        mock_method.assert_called()

def test_TrackChanged():
    dbus_manager = DbusManager(MagicMock())
    with patch.object(dbus_manager, 'TrackChanged', return_value=None) as mock_method:
        dbus_manager.TrackChanged()
        mock_method.assert_called()
