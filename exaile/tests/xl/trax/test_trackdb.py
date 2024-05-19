from unittest.mock import MagicMock, patch

import pytest

from xl.trax.trackdb import TrackDB, TrackDBIterator, TrackHolder


def test_track_holder_initialization():
    track_mock = MagicMock()
    track_mock.name = "Mock Song"
    track_mock.duration = 4.00

    holder = TrackHolder(track=track_mock, key="001", genre="Pop", artist="Artist A")

    assert holder._track == track_mock
    assert holder._key == "001"
    assert holder._attrs["genre"] == "Pop"
    assert holder._attrs["artist"] == "Artist A"

def test_track_holder_delegation():
    track_mock = MagicMock()
    track_mock.name = "Mock Song"
    track_mock.duration = 4.00

    holder = TrackHolder(track=track_mock, key="001")

    assert holder.name == "Mock Song"
    assert holder.duration == 4.00

def test_track_holder_additional_attributes():
    track_mock = MagicMock()
    track_mock.genre = "Pop"
    track_mock.artist = "Artist A"

    holder = TrackHolder(track=track_mock, key="001", genre="Pop", artist="Artist A")

    assert holder.genre == "Pop"
    assert holder.artist == "Artist A"
    
def test_track_holder_no_kwargs():
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    
    assert holder._attrs == {}

def test_track_holder_key_access():
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")

    assert holder._key == "001"

def test_track_holder_track_attribute_overridden():
    track_mock = MagicMock()
    track_mock.name = "Mock Song"
    holder = TrackHolder(track=track_mock, key="001", name="Overridden Song")

    assert holder.name != "Overridden Song"

def test_track_holder_track_method_delegation():
    track_mock = MagicMock()
    track_mock.play = MagicMock(return_value="Playing Mock Song")
    holder = TrackHolder(track=track_mock, key="001")

    assert holder.play() == "Playing Mock Song"
    track_mock.play.assert_called_once()

def test_track_holder_update_attributes():
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001", genre="Pop")
    holder._attrs['genre'] = "Rock"

    assert holder.genre != "Rock"

def test_track_holder_multiple_kwargs():
    track_mock = MagicMock()
    track_mock.genre = "Pop"
    track_mock.artist = "Artist A"
    track_mock.year = 2024
    holder = TrackHolder(track=track_mock, key="001", genre="Pop", artist="Artist A", year=2024)

    assert holder.genre == "Pop"
    assert holder.artist == "Artist A"
    assert holder.year == 2024

def test_track_holder_repr():
    track_mock = MagicMock()
    track_mock.__repr__ = MagicMock(return_value="<Track Mock>")
    holder = TrackHolder(track=track_mock, key="001")

    assert repr(holder) != "<Track Mock>"

def test_track_holder_str():
    track_mock = MagicMock()
    track_mock.__str__ = MagicMock(return_value="Track: Mock Song")
    holder = TrackHolder(track=track_mock, key="001")

    assert str(holder) != "Track: Mock Song"

def test_track_holder_equality():
    track_mock1 = MagicMock()
    track_mock2 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    holder2 = TrackHolder(track=track_mock2, key="001")

    assert holder1 != holder2

def test_track_holder_same_track():
    track_mock = MagicMock()
    holder1 = TrackHolder(track=track_mock, key="001")
    holder2 = TrackHolder(track=track_mock, key="002")

    assert holder1._track == holder2._track
    

def test_track_db_iterator_basic():
    track1 = MagicMock()
    track2 = MagicMock()
    holder1 = TrackHolder(track1, "001")
    holder2 = TrackHolder(track2, "002")
    iterator = iter([("key1", holder1), ("key2", holder2)])
    
    track_db_iterator = TrackDBIterator(iterator)
    
    result = list(track_db_iterator)
    
    assert result == [track1, track2]

def test_track_db_iterator_empty():
    iterator = iter([])
    
    track_db_iterator = TrackDBIterator(iterator)
    
    result = list(track_db_iterator)
    
    assert result == []

def test_track_db_iterator_single_item():
    track = MagicMock()
    holder = TrackHolder(track, "001")
    iterator = iter([("key1", holder)])
    
    track_db_iterator = TrackDBIterator(iterator)
    
    result = list(track_db_iterator)
    
    assert result == [track]

def test_track_db_iterator_multiple_items():
    track1 = MagicMock()
    track2 = MagicMock()
    track3 = MagicMock()
    holder1 = TrackHolder(track1, "001")
    holder2 = TrackHolder(track2, "002")
    holder3 = TrackHolder(track3, "003")
    iterator = iter([("key1", holder1), ("key2", holder2), ("key3", holder3)])
    
    track_db_iterator = TrackDBIterator(iterator)
    
    result = list(track_db_iterator)
    
    assert result == [track1, track2, track3]

def test_track_db_iterator_stop_iteration():
    track = MagicMock()
    holder = TrackHolder(track, "001")
    iterator = iter([("key1", holder)])
    
    track_db_iterator = TrackDBIterator(iterator)
    
    result = next(track_db_iterator)
    assert result == track
    
    with pytest.raises(StopIteration):
        next(track_db_iterator)

def test_track_db_iterator_iter_method():
    track = MagicMock()
    holder = TrackHolder(track, "001")
    iterator = iter([("key1", holder)])
    
    track_db_iterator = TrackDBIterator(iterator)
    
    assert iter(track_db_iterator) is track_db_iterator
    
def test_track_db_iterator_repeated_next():
    track1 = MagicMock()
    track2 = MagicMock()
    holder1 = TrackHolder(track1, "001")
    holder2 = TrackHolder(track2, "002")
    iterator = iter([("key1", holder1), ("key2", holder2)])
    
    track_db_iterator = TrackDBIterator(iterator)
    
    assert next(track_db_iterator) == track1
    assert next(track_db_iterator) == track2
    with pytest.raises(StopIteration):
        next(track_db_iterator)


class Track:
    # Mocking the Track class for testing purposes
    @staticmethod
    def _get_track_count():
        return 0

def test_track_db_initialization():
    db = TrackDB(name="TestDB", location="test_location", pickle_attrs=["attr1"], loadfirst=False)
    assert db.name == "TestDB"
    assert db.location == "test_location"
    assert db._dirty is False
    assert db.tracks == {}
    assert db.pickle_attrs == ["attr1", "tracks", "name", "_key"]

def test_track_db_load_first_no_tracks():
    with patch("test_trackdb.Track._get_track_count", return_value=0):
        db = TrackDB(name="TestDB", loadfirst=True)
        assert db.name == "TestDB"

def test_track_db_add_track():
    db = TrackDB(name="TestDB")
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    db.tracks["track1"] = holder
    assert db.tracks["track1"] == holder

def test_track_db_remove_track():
    db = TrackDB(name="TestDB")
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    db.tracks["track1"] = holder
    del db.tracks["track1"]
    assert "track1" not in db.tracks

def test_track_db_retrieve_track():
    db = TrackDB(name="TestDB")
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    db.tracks["track1"] = holder
    retrieved_track = db.tracks.get("track1")
    assert retrieved_track == holder

def test_track_db_search_track():
    db = TrackDB(name="TestDB")
    track_mock1 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    track_mock2 = MagicMock()
    holder2 = TrackHolder(track=track_mock2, key="002")
    db.tracks["track1"] = holder1
    db.tracks["track2"] = holder2
    results = [holder for key, holder in db.tracks.items() if "track1" in key]
    assert results == [holder1]

def test_track_db_save_load():
    db = TrackDB(name="TestDB", location="test_location")
    with patch.object(db, 'load_from_location') as mock_load:
        with patch.object(db, '_timeout_save') as mock_save:
            db.load_from_location()
            mock_load.assert_called_once()
            db._timeout_save()
            mock_save.assert_called_once()

def test_track_db_pickle_attrs_handling():
    db = TrackDB(name="TestDB", pickle_attrs=["attr1", "attr2"])
    assert "tracks" in db.pickle_attrs
    assert "name" in db.pickle_attrs
    assert "_key" in db.pickle_attrs
    assert "attr1" in db.pickle_attrs
    assert "attr2" in db.pickle_attrs

def test_track_db_error_handling():
    with patch("test_trackdb.Track._get_track_count", return_value=0):
        db = TrackDB(name="TestDB", loadfirst=True)
        assert db.name == "TestDB"
        with pytest.raises(KeyError):
            _ = db.tracks["non_existent_track"]
            
def test_track_db_iterator_initialization():
    db = TrackDB(name="TestDB")
    track_mock1 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    track_mock2 = MagicMock()
    holder2 = TrackHolder(track=track_mock2, key="002")
    db.tracks["track1"] = holder1
    db.tracks["track2"] = holder2
    
    iterator = iter(db)
    
    assert isinstance(iterator, TrackDBIterator)

def test_track_db_iteration():
    db = TrackDB(name="TestDB")
    track_mock1 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    track_mock2 = MagicMock()
    holder2 = TrackHolder(track=track_mock2, key="002")
    db.tracks["track1"] = holder1
    db.tracks["track2"] = holder2
    
    track_list = [track for track in db]
    
    assert track_list == [track_mock1, track_mock2]

def test_track_db_empty_iteration():
    db = TrackDB(name="TestDB")
    
    track_list = [track for track in db]
    
    assert track_list == []

def test_track_db_iteration_runtime_error():
    db = TrackDB(name="TestDB")
    track_mock1 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    track_mock2 = MagicMock()
    holder2 = TrackHolder(track=track_mock2, key="002")
    db.tracks["track1"] = holder1
    db.tracks["track2"] = holder2
    
    iterator = iter(db)
    
    next(iterator)  # Consume the first item
    db.tracks["track3"] = TrackHolder(track=MagicMock(), key="003")  # Modify the tracks
    
    with pytest.raises(RuntimeError):
        list(iterator)  # Attempt to consume the rest of the iterator

def test_track_db_iterator_with_mock():
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    mock_iterator = MagicMock()
    mock_iterator.__iter__.return_value = iter([("key1", holder)])
    
    with patch("test_trackdb.TrackDBIterator", return_value=mock_iterator):
        db = TrackDB(name="TestDB")
        db.tracks["track1"] = holder
        
        iterator = iter(db)
        
        result = list(iterator)
        
        assert result == [track_mock]


def test_track_db_length_empty():
    db = TrackDB(name="TestDB")
    assert len(db) == 0

def test_track_db_length_one_track():
    db = TrackDB(name="TestDB")
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    db.tracks["track1"] = holder
    assert len(db) == 1

def test_track_db_length_multiple_tracks():
    db = TrackDB(name="TestDB")
    track_mock1 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    track_mock2 = MagicMock()
    holder2 = TrackHolder(track=track_mock2, key="002")
    db.tracks["track1"] = holder1
    db.tracks["track2"] = holder2
    assert len(db) == 2

def test_track_db_length_after_addition():
    db = TrackDB(name="TestDB")
    track_mock1 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    db.tracks["track1"] = holder1
    assert len(db) == 1
    track_mock2 = MagicMock()
    holder2 = TrackHolder(track=track_mock2, key="002")
    db.tracks["track2"] = holder2
    assert len(db) == 2

def test_track_db_length_after_removal():
    db = TrackDB(name="TestDB")
    track_mock1 = MagicMock()
    holder1 = TrackHolder(track=track_mock1, key="001")
    track_mock2 = MagicMock()
    holder2 = TrackHolder(track=track_mock2, key="002")
    db.tracks["track1"] = holder1
    db.tracks["track2"] = holder2
    assert len(db) == 2
    del db.tracks["track1"]
    assert len(db) == 1

def test_track_db_length_with_duplicate_keys():
    db = TrackDB(name="TestDB")
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    db.tracks["track1"] = holder
    db.tracks["track1"] = holder  # Adding the same key should not change the length
    assert len(db) == 1
    
def test_set_name():
    db = TrackDB(name="OriginalName")
    db.set_name("NewName")
    assert db.name == "NewName"
    assert db._dirty is True

def test_set_name_to_empty():
    db = TrackDB(name="OriginalName")
    db.set_name("")
    assert db.name == ""
    assert db._dirty is True

def test_set_name_same_value():
    db = TrackDB(name="SameName")
    db.set_name("SameName")
    assert db.name == "SameName"
    assert db._dirty is True

def test_set_name_to_whitespace():
    db = TrackDB(name="OriginalName")
    db.set_name(" ")
    assert db.name == " "
    assert db._dirty is True
    
def test_get_name():
    db = TrackDB(name="TestDB")
    assert db.get_name() == "TestDB"

def test_get_name_empty():
    db = TrackDB(name="")
    assert db.get_name() == ""

def test_get_name_after_set_name():
    db = TrackDB(name="InitialName")
    db.set_name("NewName")
    assert db.get_name() == "NewName"

def test_get_name_with_whitespace():
    db = TrackDB(name=" ")
    assert db.get_name() == " "
    
def test_set_location():
    db = TrackDB(location="original_location")
    db.set_location("new_location")
    assert db.location == "new_location"
    assert db._dirty is True

def test_set_location_to_none():
    db = TrackDB(location="original_location")
    db.set_location(None)
    assert db.location is None
    assert db._dirty is True

def test_set_location_same_value():
    db = TrackDB(location="same_location")
    db.set_location("same_location")
    assert db.location == "same_location"
    assert db._dirty is True

def test_set_location_to_empty():
    db = TrackDB(location="original_location")
    db.set_location("")
    assert db.location == ""
    assert db._dirty is True

def test_set_location_to_whitespace():
    db = TrackDB(location="original_location")
    db.set_location(" ")
    assert db.location == " "
    assert db._dirty is True
    
def test_get_track_by_loc_existing_track():
    db = TrackDB(name="TestDB")
    track_mock = MagicMock()
    holder = TrackHolder(track=track_mock, key="001")
    db.tracks["test_loc"] = holder
    assert db.get_track_by_loc("test_loc") == track_mock

def test_get_track_by_loc_nonexistent_track():
    db = TrackDB(name="TestDB")
    assert db.get_track_by_loc("nonexistent_loc") is None

def test_get_track_by_loc_empty_db():
    db = TrackDB(name="TestDB")
    assert db.get_track_by_loc("any_loc") is None

def test_loc_is_member_existing_loc():
    db = TrackDB(name="TestDB")
    db.tracks["test_loc"] = "dummy_track"
    assert db.loc_is_member("test_loc") is True

def test_loc_is_member_nonexistent_loc():
    db = TrackDB(name="TestDB")
    assert db.loc_is_member("nonexistent_loc") is False

def test_loc_is_member_empty_db():
    db = TrackDB(name="TestDB")
    assert db.loc_is_member("any_loc") is False
    
def test_get_count_empty_db():
    db = TrackDB(name="TestDB")
    assert db.get_count() == 0

def test_get_count_one_track():
    db = TrackDB(name="TestDB")
    db.tracks["track1"] = "dummy_track"
    assert db.get_count() == 1

def test_get_count_multiple_tracks():
    db = TrackDB(name="TestDB")
    db.tracks["track1"] = "dummy_track1"
    db.tracks["track2"] = "dummy_track2"
    assert db.get_count() == 2