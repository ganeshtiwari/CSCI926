import pytest
import os
from xl import common, event, settings, trax
from collections import deque
import logging
import threading
from gi.repository import Gio
from typing import Deque, Dict, Iterable, List, MutableSequence, Optional, Set, Tuple
from unittest.mock import patch, MagicMock, PropertyMock, ANY, call
from xl.collection import get_collection_by_loc, COLLECTIONS, CollectionScanThread, Collection, Library, event, LibraryMonitor, deque, TransferQueue

def test_get_collection_loc_found():
    collection_mock = MagicMock()
    collection_mock.loc_is_member.return_value = True
    COLLECTIONS.add(collection_mock)    
    result = get_collection_by_loc('some_location')
    assert result is collection_mock
    COLLECTIONS.remove(collection_mock)

def test_get_collection_loc_notFound():
    result = get_collection_by_loc('nonexistent_location')
    assert result is None

def test_collection_scanThread_init():
    collection_mock = MagicMock()
    thread = CollectionScanThread(collection=collection_mock, startup_scan=True, force_update=False)    
    assert thread.collection == collection_mock
    assert thread.startup_scan == True
    assert thread.force_update == False

def test_collection_scanThread_stop():
    collection_mock = MagicMock()
    thread = CollectionScanThread(collection=collection_mock)
    with patch.object(thread, 'stop', wraps=thread.stop) as stop_patch:
        thread.stop()
        stop_patch.assert_called_once()
        collection_mock.stop_scan.assert_called_once()

def test_collection_scanThread_run():
    collection_mock = MagicMock()
    thread = CollectionScanThread(collection=collection_mock)    
    with patch('xl.collection.event.add_callback') as mock_add, \
         patch('xl.collection.event.remove_callback') as mock_remove:
        thread.run()
        mock_add.assert_called_once()
        mock_remove.assert_called_once()
        collection_mock.rescan_libraries.assert_called_once_with(
            startup_only=thread.startup_scan, force_update=thread.force_update
        )

def test_on_scan_progress_update_emits():
    collection_mock = MagicMock()
    thread = CollectionScanThread(collection=collection_mock)    
    with patch.object(thread, 'emit') as mock_emit:
        thread.on_scan_progress_update('scan_progress_update', collection_mock, 50)
        mock_emit.assert_called_with('progress-update', 50)

def test_on_scan_progress_update_emitsDone():
    collection_mock = MagicMock()
    thread = CollectionScanThread(collection=collection_mock)    
    with patch.object(thread, 'emit') as mock_emit:
        thread.on_scan_progress_update('scan_progress_update', collection_mock, 100)
        mock_emit.assert_called_with('done')

def test_collection_init():
    collection = Collection("Test Collection")
    assert collection.name == "Test Collection"
    assert collection in COLLECTIONS

def test_add_library():
    collection = Collection("Test Collection")
    library = MagicMock()
    library.get_location.return_value = "location"    
    with patch.object(collection, 'serialize_libraries') as mock_serialize:
        collection.add_library(library)
        assert collection.libraries["location"] == library
        mock_serialize.assert_called_once()

def test_remove_library():
    collection = Collection("Test Collection")
    library = MagicMock()
    library.get_location.return_value = "location"
    collection.libraries["location"] = library
    with patch.object(collection, 'serialize_libraries') as mock_serialize:
        collection.remove_library(library)
        assert "location" not in collection.libraries
        mock_serialize.assert_called_once()

def test_freeze_libraries():
    collection = Collection("Test Collection")
    collection.freeze_libraries()
    assert collection._frozen is True

def test_thaw_libraries():
    collection = Collection("Test Collection")
    collection.freeze_libraries()
    collection._libraries_dirty = True
    with patch('xl.collection.event.log_event') as mock_log_event:
        collection.thaw_libraries()
        assert collection._frozen is False
        mock_log_event.assert_called_with('libraries_modified', collection, None)

def test_stop_scan():
    collection = Collection("Test Collection")
    collection.stop_scan()
    assert collection._scan_stopped is True

def test_rescan_libraries_noLibraries():
    collection = Collection("Test Collection")
    with patch('xl.collection.event.log_event') as mock_log_event:
        collection.rescan_libraries()
        mock_log_event.assert_called_with('scan_progress_update', collection, 100)

def test_rescan_libraries_scanning():
    collection = Collection("Test Collection")
    collection._scanning = True
    with pytest.raises(Exception, match="Collection is already being scanned"):
        collection.rescan_libraries()

def test_serialize_unserialize_libraries():
    collection = Collection("Test Collection")
    library = MagicMock()
    library.location = "loc"
    library.monitored = True
    library.realtime = False
    library.scan_interval = 30
    library.startup_scan = True
    collection.libraries["loc"] = library
    serialized = collection.serialize_libraries()
    assert isinstance(serialized, list)
    assert serialized[0]['location'] == "loc"
    collection.unserialize_libraries(serialized)
    assert "loc" in collection.libraries
    assert collection.libraries["loc"].location == "loc"

def test_progress_update():
    collection = Collection("Test Collection")
    collection.file_count = 100
    library = MagicMock()
    with patch('xl.collection.event.log_event') as mock_log_event:
        collection._progress_update('tracks_scanned', library, 10)
        mock_log_event.assert_called_once()
        assert collection._running_count == 10

def test_close_collection():
    collection = Collection("Test Collection")
    original_collections = COLLECTIONS.copy()
    try:
        with patch('xl.collection.COLLECTIONS', new_callable=set) as mock_collections:
            mock_collections.update(original_collections)
            mock_collections.add(collection)
            collection.close()
            assert collection not in mock_collections
    finally:
        COLLECTIONS.clear()
        COLLECTIONS.update(original_collections)

def test_delete_tracks():
    collection = Collection("Test Collection")
    track = MagicMock()
    library = MagicMock()
    collection.libraries["loc"] = library
    with patch.object(library, 'delete') as mock_delete:
        collection.delete_tracks([track])
        mock_delete.assert_called_once_with(track.get_loc_for_io())

def test_get_libraries():
    collection = Collection("Test Collection")
    library1 = MagicMock()
    library2 = MagicMock()
    collection.libraries['loc1'] = library1
    collection.libraries['loc2'] = library2
    libraries = collection.get_libraries()
    assert libraries == [library1, library2]

def test_count_files():
    collection = Collection("Test Collection")
    library1 = MagicMock()
    library2 = MagicMock()
    library1._count_files.return_value = 10
    library2._count_files.return_value = 20
    collection.libraries['loc1'] = library1
    collection.libraries['loc2'] = library2
    with patch('xl.collection.logger.debug') as mock_debug:
        collection._Collection__count_files()
        assert collection.file_count == 30
        mock_debug.assert_called_with("File count: %s", 30)

def test_get_monitored():
    library = MagicMock()
    library.location = 'file:///test/library'
    monitor = LibraryMonitor(library)
    monitor.set_property('monitored', False)
    assert monitor.get_property('monitored') is False

def test_set_monitored():
    library = MagicMock()
    library.location = 'file:///test/library'
    monitor = LibraryMonitor(library)
    monitor.set_property('monitored', True)
    assert monitor.get_property('monitored') is True


def test_library_monitor_signals():
    library = MagicMock()
    library.location = 'file:///test/library'
    monitor = LibraryMonitor(library)
    with patch.object(monitor, 'emit') as mock_emit:
        monitor.emit('location-added', MagicMock())
        mock_emit.assert_called_once_with('location-added', ANY)
        mock_emit.reset_mock()
        monitor.emit('location-removed', MagicMock())
        mock_emit.assert_called_once_with('location-removed', ANY)

def test_on_location_changed():
    library = MagicMock()
    library.location = 'file:///test/library'
    monitor = LibraryMonitor(library)
    mock_monitor = MagicMock()
    gfile = MagicMock()
    gfile.get_uri.return_value = 'file:///test/file'
    monitor.on_location_changed(mock_monitor, gfile, None, Gio.FileMonitorEvent.CREATED)
    with patch('xl.trax.util.get_tracks_from_uri') as mock_get_tracks:
        mock_get_tracks.return_value = []
        monitor._LibraryMonitor__process_change_queue(gfile)
        mock_get_tracks.assert_called_once_with('file:///test/file')

def test_library_init():
    library = Library("file:///test/library")
    assert library.location == "file:///test/library"
    assert library.scan_interval == 0
    assert not library._startup_scan

def test_set_location():
    library = Library("file:///initial/location")
    library.set_location("file:///new/location")
    assert library.location == "file:///new/location"

def test_get_location():
    library = Library("file:///initial/location")
    assert library.get_location() == "file:///initial/location"

def test_set_monitored_lib():
    library = Library("file:///test/library")
    library.collection = MagicMock()
    library.set_monitored(True)
    assert library.monitor.props.monitored is True
    library.collection.serialize_libraries.assert_called_once()

def test_get_monitored_lib():
    library = Library("file:///test/library")
    library.monitor = MagicMock()
    library.monitor.props.monitored = True
    assert library.get_monitored() is True

def test_set_rescan_interval():
    library = Library("file:///test/library")
    library.set_rescan_interval(3600)
    assert library.scan_interval == 3600

def test_get_rescan_interval():
    library = Library("file:///test/library")
    library.scan_interval = 3600
    assert library.get_rescan_interval() == 3600

def test_set_startup_scan():
    library = Library("file:///test/library")
    library.collection = MagicMock()
    library.set_startup_scan(True)
    assert library._startup_scan is True
    library.collection.serialize_libraries.assert_called_once()

def test_get_startup_scan():
    library = Library("file:///test/library")
    library._startup_scan = True
    assert library.get_startup_scan() is True

def test_rescan():
    library = Library("file:///test/library")
    library.collection = MagicMock()
    library.collection._scan_stopped = False
    with patch('gi.repository.Gio.File.new_for_uri') as mock_new_for_uri:
        mock_file = MagicMock()
        mock_new_for_uri.return_value = mock_file
        mock_file.query_info.return_value.get_file_type.return_value = Gio.FileType.REGULAR
        with patch('xl.collection.common.walk') as mock_walk:
            mock_walk.return_value = [mock_file]
            assert library.rescan() is False

def test_delete():
    library = Library("file:///test/library")
    library.collection = MagicMock()    
    loc = "file:///test/library/file.mp3"
    with patch('gi.repository.Gio.File.new_for_uri') as mock_new_for_uri:
        file = MagicMock()
        mock_new_for_uri.return_value = file
        file.delete.return_value = True
        library.delete(loc)
        library.collection.remove.assert_called_once()

def test_count_files_lib():
    library = Library("file:///test/library")
    library.collection = MagicMock()
    library.collection._scan_stopped = False
    with patch('xl.collection.common.walk') as mock_walk:
          mock_walk.return_value = [MagicMock(), MagicMock(), MagicMock()]
          assert library._count_files() == 3

def test_transfer_tracks_successfully():
    library = MagicMock()
    queue = TransferQueue(library)
    tracks = [MagicMock(), MagicMock()]
    queue.enqueue(tracks)
    with patch('xl.collection.event.log_event') as mock_log_event:
        queue.transfer()
        assert not queue.queue
        assert not queue.transferring
        assert mock_log_event.call_args_list == [
        call('track_transfer_progress', queue, 0.0),
        call('track_transfer_progress', queue, 50.0),
        call('track_transfer_progress', queue, 100)
        ]


def test_cancel_transfer():
    library = MagicMock()
    queue = TransferQueue(library)
    queue.transfer()
    queue.cancel()
    assert queue._stop


def test_count_files_scanStopped():
    library = Library("file:///test/library")
    library.collection = MagicMock()
    library.collection._scan_stopped = True
    with patch('xl.collection.common.walk') as mock_walk:
        mock_walk.return_value = [MagicMock(), MagicMock(), MagicMock()]
        assert library._count_files() == 0

def test_check_compilation():
    library = Library("file:///test/library")
    ccheck = {}
    compilations = []
    track1 = MagicMock()
    track1.get_tag_raw.side_effect = lambda tag: {
        '__basedir': 'dir1',
        'album': 'album1',
        'artist': 'artist1'
    }[tag]
    track2 = MagicMock()
    track2.get_tag_raw.side_effect = lambda tag: {
        '__basedir': 'dir1',
        'album': 'album1',
        'artist': 'artist2'
    }[tag]
    library._check_compilation(ccheck, compilations, track1)
    library._check_compilation(ccheck, compilations, track2)
    assert ('dir1', 'album1') in compilations

def test_check_no_compilation():
    library = Library("file:///test/library")
    ccheck = {}
    compilations = []
    track = MagicMock()
    with patch('xl.collection.settings.get_option', return_value=False):
        library._check_compilation(ccheck, compilations, track)
        assert compilations == []

def test_update_track():
    library = Library("file:///test/library")
    library.collection = MagicMock()
    gfile = MagicMock()
    gfile.get_uri.return_value = "file:///test/track.mp3"
    track = MagicMock()
    library.collection.get_track_by_loc.return_value = track
    with patch('xl.trax.Track') as mock_track:
        result = library.update_track(gfile, force_update=True)
        track.read_tags.assert_called_once_with(force=True)
        assert result is track

def test_update_track_no_uri():
    library = Library("file:///test/library")
    library.collection = MagicMock()
    gfile = MagicMock()
    gfile.get_uri.return_value = None
    result = library.update_track(gfile)
    assert result is None

def test_enqueue_single_track():
    library = MagicMock()
    queue = TransferQueue(library)
    track = MagicMock()
    queue.enqueue([track])
    assert queue.queue == [track]

def test_enqueue_multiple_tracks():
    library = MagicMock()
    queue = TransferQueue(library)
    tracks = [MagicMock(), MagicMock()]
    queue.enqueue(tracks)
    assert queue.queue == tracks

def test_dequeue_transferring_exception():
    library = MagicMock()
    queue = TransferQueue(library)
    track = MagicMock()
    queue.enqueue([track])
    queue.transferring = True
    with pytest.raises(Exception, match="Cannot remove tracks while transferring"):
        queue.dequeue([track])

def test_dequeue_single_track():
    library = MagicMock()
    queue = TransferQueue(library)
    track = MagicMock()
    queue.enqueue([track])
    queue.dequeue([track])
    assert not queue.queue

def test_dequeue_nonexistent_track():
    library = MagicMock()
    queue = TransferQueue(library)
    track1 = MagicMock()
    track2 = MagicMock()
    queue.enqueue([track1])
    queue.dequeue([track2])
    assert queue.queue == [track1]
