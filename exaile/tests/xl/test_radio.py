import pytest
import os
from xl.radio import RadioManager, RadioList, RadioItem
from unittest.mock import patch, mock_open, MagicMock, call, PropertyMock
from xl import playlist, event, providers, trax

class Playlist:
    def __init__(self, tracks):
        self.tracks = tracks

    def get_tracks(self):
        return self.tracks

class MockRadioStation:
    def __init__(self, name):
        self.name = name

    def search(self, keyword):
        return "Mock search result"

    def get_lists(self, no_cache=False):
        return ["Mock List"]

    def load_lists(self):
        return ["Mock Load List"]

def test_radio_manager_init():
    manager = RadioManager()
    assert isinstance(manager, RadioManager)
    assert manager.stations == {}

@patch('xl.providers.register')
def test_add_station(mock_register):
    manager = RadioManager()
    station = MockRadioStation(name="Station1")
    manager.add_station(station)
    mock_register.assert_called_once_with(manager.servicename, station)

@patch('xl.providers.unregister')
def test_remove_station(mock_unregister):
    manager = RadioManager()
    station = MockRadioStation(name="Station1")
    manager.add_station(station)
    manager.remove_station(station)
    mock_unregister.assert_called_once_with(manager.servicename, station)

@patch('xl.event.log_event')
def test_on_provider_added(mock_log_event):
    manager = RadioManager()
    station = MockRadioStation(name="New Station")
    manager.on_provider_added(station)
    assert station.name in manager.stations
    mock_log_event.assert_called_once_with('station_added', manager, station)

@patch('xl.event.log_event')
def test_on_provider_removed(mock_log_event):
    manager = RadioManager()
    station = MockRadioStation(name="Existing Station")
    manager.on_provider_added(station)
    mock_log_event.reset_mock()
    manager.on_provider_removed(station)
    assert station.name not in manager.stations
    mock_log_event.assert_called_once_with('station_removed', manager, station)

def test_search_station_exists():
    manager = RadioManager()
    station = MockRadioStation(name="Searchable Station")
    manager.add_station(station)
    with patch.object(station, 'search', return_value="Found") as mock_search:
        result = manager.search(station.name, "keyword")
        mock_search.assert_called_once_with("keyword")
        assert result == "Found"

def test_search_station_nonExist():
    manager = RadioManager()
    result = manager.search("Nonexistent Station", "keyword")
    assert result is None

def test_get_lists_station_exists():
    manager = RadioManager()
    station = MockRadioStation(name="List Station")
    manager.add_station(station)
    with patch.object(station, 'get_lists', return_value=["List1", "List2"]) as mock_get_lists:
        result = manager.get_lists(station.name)
        mock_get_lists.assert_called_once_with(no_cache=False)
        assert result == ["List1", "List2"]

def test_get_lists_station_nonExist():
    manager = RadioManager()
    result = manager.get_lists("Nonexistent Station")
    assert result is None

def test_load_lists_station_exists():
    manager = RadioManager()
    station = MockRadioStation(name="Loadable Station")
    manager.add_station(station)
    with patch.object(station, 'load_lists', return_value=["List1", "List2"]) as mock_load_lists:
        result = manager.load_lists(station.name)
        mock_load_lists.assert_called_once()
        assert result == ["List1", "List2"]

def test_load_lists_station_nonExist():
    manager = RadioManager()
    result = manager.load_lists("Nonexistent Station")
    assert result is None

def test_radio_list_init():
    radio_list = RadioList(name="Favorite Songs", station="Station1")
    assert radio_list.name == "Favorite Songs"
    assert radio_list.station == "Station1"

def test_set_and_get_name():
    radio_list = RadioList(name="Initial Name")
    radio_list.set_name("New Name")
    assert radio_list.get_name() == "New Name"

def test_get_items():
    radio_list = RadioList(name="List")
    items = radio_list.get_items()
    assert isinstance(items, list)
    assert items == []

def test_string_representation():
    radio_list = RadioList(name="My Playlist")
    assert str(radio_list) == "My Playlist"

def test_radio_item_init():
    radio_item = RadioItem(name="Favorite Song", station="Station1")
    assert radio_item.name == "Favorite Song"
    assert radio_item.station == "Station1"

@patch('xl.radio.trax.Track')
@patch('xl.radio.playlist.Playlist')
def test_get_playlist(mock_playlist, mock_track):
    mock_track_instance = mock_track.return_value
    mock_track_instance.__getitem__.side_effect = lambda key: 'Test Track' if key == 'title' else None
    mock_playlist_instance = mock_playlist.return_value
    mock_playlist_instance.add_tracks = MagicMock()
    radio_item = RadioItem(name="Item")
    result_playlist = radio_item.get_playlist()
    mock_track.assert_called_once()
    mock_playlist.assert_called_once_with('Test Playlist')
    mock_playlist_instance.add_tracks.assert_called_once_with([mock_track_instance])
    assert result_playlist == mock_playlist_instance

def test_string_representation():
    radio_item = RadioItem(name="My Favorite Song")
    assert str(radio_item) == "My Favorite Song"
