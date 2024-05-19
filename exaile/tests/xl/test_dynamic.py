import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
from xl.dynamic import DynamicManager, DynamicSource

def test_dynamic_manager_init():
    pre_filled_collection = ['Track1', 'Track2', 'Track3']
    manager = DynamicManager(collection=pre_filled_collection)
    assert manager.collection == pre_filled_collection

@patch('xl.trax.search.search_tracks_from_string')
@patch.object(DynamicManager, 'find_similar_artists')
def test_find_similar_tracks_noArtists(mock_find_artists, mock_search_tracks):
    manager = DynamicManager()
    mock_find_artists.return_value = []
    tracks = manager.find_similar_tracks("TrackX", limit=1)
    assert tracks == []

@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", return_value=True)
def test_save_info_empty(mock_exists, mock_file):
    manager = DynamicManager()
    track = MagicMock()
    track.get_tag_raw.return_value = ["Artist1"]
    
    manager._save_info(track, [])
    mock_file.assert_not_called()

def test_dynamic_source_init():
    source = DynamicSource()
    assert source is not None

def test_get_results_notImplemented():
    source = DynamicSource()
    with pytest.raises(NotImplementedError):
        source.get_results("Any Artist")

def test_set_manager():
    source = DynamicSource()
    manager = DynamicManager()
    source._set_manager(manager)
    assert source.manager == manager

