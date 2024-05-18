import types
from unittest.mock import MagicMock, patch

import pytest

from xl.trax.search import _ExactMatcher, _GtMatcher, _InMatcher, _LtMatcher, _ManyMultiMetaMatcher, _Matcher, _MultiMetaMatcher, _NotMetaMatcher, _OrMetaMatcher, _RegexMatcher, SearchResultTrack, TracksInList, TracksMatcher, TracksNotInList, match_track_from_string, search_tracks, search_tracks_from_string


def test_search_result_track_initialization():
    track = MagicMock()
    track.title = "Test Song"
    track.artist = "Test Artist"
    
    search_result_track = SearchResultTrack(track)
    
    assert search_result_track.track == track, "Track attribute not set correctly"
    
def test_search_result_track_add_tags():
    track = MagicMock()
    track.title = "Test Song"
    track.artist = "Test Artist"
    
    search_result_track = SearchResultTrack(track)
    
    search_result_track.on_tags.append("rock")
    search_result_track.on_tags.append("2024")
    
    assert search_result_track.on_tags == ["rock", "2024"], "Tags not added correctly"

def test_matcher_initialization_with_lowering():
    mock_lower = MagicMock()
    mock_lower.return_value = "lowered content"
    
    matcher = _Matcher(tag="example", content="CONTENT", lower=mock_lower)
    
    assert matcher.tag == "example", "Tag attribute not set correctly"
    
    mock_lower.assert_called_once_with("CONTENT")
    assert matcher.content == "lowered content", "Content attribute not processed correctly"
    
    assert matcher.lower == mock_lower, "Lower attribute not set correctly"

def test_matcher_initialization_without_lowering():
    mock_lower = MagicMock()
    
    matcher = _Matcher(tag="__example", content="CONTENT", lower=mock_lower)
    
    assert matcher.tag == "__example", "Tag attribute not set correctly"
    
    mock_lower.assert_not_called()
    assert matcher.content == "CONTENT", "Content attribute should not be processed"
    
    assert matcher.lower == mock_lower, "Lower attribute not set correctly"


class TestMatcher(_Matcher):
    def _matches(self, value):
        return value == self.content

def test_match_found():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()

    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["TEST VALUE"]

    matcher = TestMatcher(tag="test", content="test value", lower=mock_lower)
    
    result = matcher.match(mock_srtrack)
    
    assert result == True, "Match should be found"
    mock_lower.assert_any_call("TEST VALUE")

def test_match_not_found():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]

    matcher = TestMatcher(tag="test", content="test value", lower=mock_lower)
    
    result = matcher.match(mock_srtrack)
    

    assert result == False, "Match should not be found"
    mock_lower.assert_any_call("NON MATCHING VALUE")

def test_match_null_value():
    mock_lower = MagicMock()

    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
  
    matcher = TestMatcher(tag="test", content="test value", lower=mock_lower)

    result = matcher.match(mock_srtrack)

    assert result == False, "Match should not be found"
    mock_lower.assert_called_once()

def test_exact_matcher_string_match():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["TEST VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_exact_matcher_string_match_1():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["TEST VALUE 1"]
    matcher = _ExactMatcher(tag="test", content="test value 1", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_exact_matcher_string_match_2():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["TEST VALUE 2"]
    matcher = _ExactMatcher(tag="test", content="test value 2", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_exact_matcher_string_match_3():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["TEST VALUE 3"]
    matcher = _ExactMatcher(tag="test", content="test value 3", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_exact_matcher_string_no_match():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_string_no_match_1():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value 1", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_string_no_match_2():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value 2", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_string_no_match_3():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value 3", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_string_no_match_4():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value 4", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_string_no_match_5():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value 5", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_string_no_match_6():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["NON MATCHING VALUE"]
    matcher = _ExactMatcher(tag="test", content="test value 6", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False
    
def test_exact_matcher_numeric_approximate_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["123.00005"]
    matcher = _ExactMatcher(tag="__num", content="123.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_approximate_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["123.00005"]
    matcher = _ExactMatcher(tag="__num", content="123.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_approximate_match_1():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["1.00005"]
    matcher = _ExactMatcher(tag="__num", content="1.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_exact_matcher_numeric_approximate_match_2():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["5.00005"]
    matcher = _ExactMatcher(tag="__num", content="5.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_approximate_match_3():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["-1.00005"]
    matcher = _ExactMatcher(tag="__num", content="-1.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_approximate_match_4():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["9.00005"]
    matcher = _ExactMatcher(tag="__num", content="9.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_approximate_match_5():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["0.00005"]
    matcher = _ExactMatcher(tag="__num", content="0.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_approximate_match_6():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["-1000.00005"]
    matcher = _ExactMatcher(tag="__num", content="-1000.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_approximate_match_7():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["54.00005"]
    matcher = _ExactMatcher(tag="__num", content="54.00000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_no_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["124.0001"]
    matcher = _ExactMatcher(tag="__num", content="123.0000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_no_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["124.0001"]
    matcher = _ExactMatcher(tag="__num", content="123.0000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_no_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["124.0001"]
    matcher = _ExactMatcher(tag="__num", content="123.0000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_null_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
    matcher = _ExactMatcher(tag="test", content="test value", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False
    mock_lower.assert_called_once()

def test_exact_matcher_null_value_1():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
    matcher = _ExactMatcher(tag="test", content="test value 1", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False
    mock_lower.assert_called_once()

def test_exact_matcher_null_value_2():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
    matcher = _ExactMatcher(tag="test", content="test value 2", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False
    mock_lower.assert_called_once()

def test_exact_matcher_numeric_no_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["124.0001"]
    matcher = _ExactMatcher(tag="__num", content="123.0000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_no_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["124.0001"]
    matcher = _ExactMatcher(tag="__num", content="123.0000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_no_match_1():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["11.0001"]
    matcher = _ExactMatcher(tag="__num", content="10.0000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_exact_matcher_numeric_no_match_2():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["0.0001"]
    matcher = _ExactMatcher(tag="__num", content="0.0000", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False
    
def test_in_matcher_string_match():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["This is a test string"]
    matcher = _InMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_in_matcher_string_no_match():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["No match here"]
    matcher = _InMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_in_matcher_empty_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = [""]
    matcher = _InMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_in_matcher_null_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
    matcher = _InMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_in_matcher_type_error():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = [12345]
    matcher = _InMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_regex_matcher_string_match():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["This is a test string"]
    matcher = _RegexMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_regex_matcher_string_no_match():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["No match here"]
    matcher = _RegexMatcher(tag="test", content="notfound", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_regex_matcher_case_insensitive_match():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["This is a Test String"]
    matcher = _RegexMatcher(tag="test", content="test string", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True
    
def test_regex_matcher_special_characters():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["Special characters: !@#$%^&*()"]
    matcher = _RegexMatcher(tag="test", content=r"\!@\#\$\%\^\&\*\(\)", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_regex_matcher_numeric_string_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["The number is 12345"]
    matcher = _RegexMatcher(tag="test", content=r"\d+", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_regex_matcher_numeric_string_no_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["No numbers here"]
    matcher = _RegexMatcher(tag="test", content=r"\d+", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_regex_matcher_empty_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = [""]
    matcher = _RegexMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_regex_matcher_null_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
    matcher = _RegexMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_regex_matcher_type_error():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = [12345]
    matcher = _RegexMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_regex_matcher_multiple_matches():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["test", "another test", "no match"]
    matcher = _RegexMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_regex_matcher_no_valid_matches():
    mock_lower = MagicMock()
    mock_lower.side_effect = lambda x: x.lower()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["nope", "nothing", "not here"]
    matcher = _RegexMatcher(tag="test", content="test", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False
    
def test_gt_matcher_numeric_gt_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["10"]
    matcher = _GtMatcher(tag="test", content="5", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_gt_matcher_numeric_lt_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["5"]
    matcher = _GtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_gt_matcher_numeric_eq_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["10"]
    matcher = _GtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_gt_matcher_non_numeric():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["not a number"]
    matcher = _GtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_gt_matcher_empty_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = [""]
    matcher = _GtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_gt_matcher_null_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
    matcher = _GtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_lt_matcher_numeric_lt_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["5"]
    matcher = _LtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_lt_matcher_numeric_gt_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["10"]
    matcher = _LtMatcher(tag="test", content="5", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_lt_matcher_numeric_eq_match():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["10"]
    matcher = _LtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_lt_matcher_non_numeric():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = ["not a number"]
    matcher = _LtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_lt_matcher_empty_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = [""]
    matcher = _LtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == False

def test_lt_matcher_null_value():
    mock_lower = MagicMock()
    mock_srtrack = MagicMock()
    mock_srtrack.track.get_tag_search.return_value = "__null__"
    matcher = _LtMatcher(tag="test", content="10", lower=mock_lower)
    result = matcher.match(mock_srtrack)
    assert result == True

def test_not_meta_matcher_positive():
    mock_matcher = MagicMock()
    mock_matcher.match.return_value = True
    not_matcher = _NotMetaMatcher(matcher=mock_matcher)
    result = not_matcher.match(MagicMock())
    assert result == False

def test_not_meta_matcher_negative():
    mock_matcher = MagicMock()
    mock_matcher.match.return_value = False
    not_matcher = _NotMetaMatcher(matcher=mock_matcher)
    result = not_matcher.match(MagicMock())
    assert result == True


def test_or_meta_matcher_both_false():
    mock_left = MagicMock()
    mock_left.match.return_value = False
    mock_right = MagicMock()
    mock_right.match.return_value = False
    or_matcher = _OrMetaMatcher(left=mock_left, right=mock_right)
    result = or_matcher.match(MagicMock())
    assert result == False

def test_or_meta_matcher_left_true():
    mock_left = MagicMock()
    mock_left.match.return_value = True
    mock_right = MagicMock()
    mock_right.match.return_value = False
    or_matcher = _OrMetaMatcher(left=mock_left, right=mock_right)
    result = or_matcher.match(MagicMock())
    assert result == True

def test_or_meta_matcher_right_true():
    mock_left = MagicMock()
    mock_left.match.return_value = False
    mock_right = MagicMock()
    mock_right.match.return_value = True
    or_matcher = _OrMetaMatcher(left=mock_left, right=mock_right)
    result = or_matcher.match(MagicMock())
    assert result == True

def test_or_meta_matcher_both_true():
    mock_left = MagicMock()
    mock_left.match.return_value = True
    mock_right = MagicMock()
    mock_right.match.return_value = True
    or_matcher = _OrMetaMatcher(left=mock_left, right=mock_right)
    result = or_matcher.match(MagicMock())
    assert result == True

def test_multi_meta_matcher_all_true():
    mock_matchers = [MagicMock(), MagicMock(), MagicMock()]
    for mock_matcher in mock_matchers:
        mock_matcher.match.return_value = True
    multi_matcher = _MultiMetaMatcher(matchers=mock_matchers)
    result = multi_matcher.match(MagicMock())
    assert result == True

def test_multi_meta_matcher_one_false():
    mock_matchers = [MagicMock(), MagicMock(), MagicMock()]
    mock_matchers[1].match.return_value = False
    for i, mock_matcher in enumerate(mock_matchers):
        if i != 1:
            mock_matcher.match.return_value = True
    multi_matcher = _MultiMetaMatcher(matchers=mock_matchers)
    result = multi_matcher.match(MagicMock())
    assert result == False

def test_multi_meta_matcher_all_false():
    mock_matchers = [MagicMock(), MagicMock(), MagicMock()]
    for mock_matcher in mock_matchers:
        mock_matcher.match.return_value = False
    multi_matcher = _MultiMetaMatcher(matchers=mock_matchers)
    result = multi_matcher.match(MagicMock())
    assert result == False

def test_multi_meta_matcher_empty():
    multi_matcher = _MultiMetaMatcher(matchers=[])
    result = multi_matcher.match(MagicMock())
    assert result == True
    
def test_many_multi_meta_matcher_all_true():
    mock_matchers = [MagicMock(), MagicMock(), MagicMock()]
    for mock_matcher in mock_matchers:
        mock_matcher.match.return_value = True
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=mock_matchers)
    result = many_multi_matcher.match(MagicMock())
    assert result == True

def test_many_multi_meta_matcher_one_false():
    mock_matchers = [MagicMock(), MagicMock(), MagicMock()]
    mock_matchers[1].match.return_value = False
    for i, mock_matcher in enumerate(mock_matchers):
        if i != 1:
            mock_matcher.match.return_value = True
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=mock_matchers)
    result = many_multi_matcher.match(MagicMock())
    assert result == True

def test_many_multi_meta_matcher_all_false():
    mock_matchers = [MagicMock(), MagicMock(), MagicMock()]
    for mock_matcher in mock_matchers:
        mock_matcher.match.return_value = False
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=mock_matchers)
    result = many_multi_matcher.match(MagicMock())
    assert result == False

def test_many_multi_meta_matcher_empty():
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=[])
    result = many_multi_matcher.match(MagicMock())
    assert result == False
    
def test_many_multi_meta_matcher_with_tag():
    mock_matcher1 = MagicMock()
    mock_matcher1.tag = "tag1"
    mock_matcher1.match.return_value = True
    mock_matcher2 = MagicMock()
    mock_matcher2.tag = "tag2"
    mock_matcher2.match.return_value = False
    mock_matcher3 = MagicMock()
    mock_matcher3.tag = "tag3"
    mock_matcher3.match.return_value = True
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=[mock_matcher1, mock_matcher2, mock_matcher3])
    result = many_multi_matcher.match(MagicMock())
    assert result == True
    assert many_multi_matcher.tags == {"tag1", "tag3"}

def test_many_multi_meta_matcher_with_multiple_tags():
    mock_matcher1 = MagicMock()
    mock_matcher1.tags = {"tag1", "tag2"}
    mock_matcher1.match.return_value = True
    mock_matcher2 = MagicMock()
    mock_matcher2.tags = {"tag3"}
    mock_matcher2.match.return_value = False
    mock_matcher3 = MagicMock()
    mock_matcher3.tags = set()
    mock_matcher3.match.return_value = True
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=[mock_matcher1, mock_matcher2, mock_matcher3])
    result = many_multi_matcher.match(MagicMock())
    assert result == True

def test_many_multi_meta_matcher_with_empty_tags():
    mock_matcher1 = MagicMock()
    mock_matcher1.tags = set()
    mock_matcher1.match.return_value = True
    mock_matcher2 = MagicMock()
    mock_matcher2.tags = set()
    mock_matcher2.match.return_value = False
    mock_matcher3 = MagicMock()
    mock_matcher3.tags = set()
    mock_matcher3.match.return_value = True
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=[mock_matcher1, mock_matcher2, mock_matcher3])
    result = many_multi_matcher.match(MagicMock())
    assert result == True

def test_many_multi_meta_matcher_without_tag():
    mock_matcher1 = MagicMock()
    mock_matcher1.tag = "tag1"
    mock_matcher1.match.return_value = True
    mock_matcher2 = MagicMock()
    mock_matcher2.tag = None
    mock_matcher2.match.return_value = False
    mock_matcher3 = MagicMock()
    mock_matcher3.tag = "tag3"
    mock_matcher3.match.return_value = True
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=[mock_matcher1, mock_matcher2, mock_matcher3])
    result = many_multi_matcher.match(MagicMock())
    assert result == True
    assert many_multi_matcher.tags == {"tag1", "tag3"}

def test_many_multi_meta_matcher_all_false_with_tags():
    mock_matcher1 = MagicMock()
    mock_matcher1.tag = "tag1"
    mock_matcher1.match.return_value = False
    mock_matcher2 = MagicMock()
    mock_matcher2.tag = "tag2"
    mock_matcher2.match.return_value = False
    mock_matcher3 = MagicMock()
    mock_matcher3.tag = "tag3"
    mock_matcher3.match.return_value = False
    many_multi_matcher = _ManyMultiMetaMatcher(matchers=[mock_matcher1, mock_matcher2, mock_matcher3])
    result = many_multi_matcher.match(MagicMock())
    assert result == False
    assert many_multi_matcher.tags == set()

def test_tracks_matcher_case_sensitive():
    search_string = "track name: test Track1"
    matcher = TracksMatcher(search_string=search_string, case_sensitive=True)
    assert matcher.case_sensitive == True

def test_tracks_matcher_case_insensitive():
    search_string = "track name: test Track1"
    matcher = TracksMatcher(search_string=search_string, case_sensitive=False)
    assert matcher.case_sensitive == False

def test_tracks_matcher_keyword_tags():
    search_string = "track name: test Track1"
    keyword_tags = ["tag1", "tag2"]
    matcher = TracksMatcher(search_string=search_string, keyword_tags=keyword_tags)
    assert matcher.keyword_tags == keyword_tags

def test_tracks_matcher_default_keyword_tags():
    search_string = "track name: test Track1"
    matcher = TracksMatcher(search_string=search_string)
    assert matcher.keyword_tags == []

def test_tracks_matcher_tokenization():
    search_string = "track name: test Track1"
    matcher = TracksMatcher(search_string=search_string)
    assert matcher.matchers is not None

def test_tracks_matcher_red():
    search_string = "track name: test Track1"
    matcher = TracksMatcher(search_string=search_string)
    assert matcher.matchers is not None

def test_tracks_matcher_optimize_tokens():
    search_string = "track name: test Track1"
    matcher = TracksMatcher(search_string=search_string)
    assert matcher.matchers is not None

def test_tracks_matcher_tokens_to_matchers():
    search_string = "track name: test Track1"
    matcher = TracksMatcher(search_string=search_string)
    assert matcher.matchers is not None

def test_append_matcher_without_or_match():
    matcher1 = MagicMock()
    matcher2 = MagicMock()
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.append_matcher(matcher1, or_match=False)
    tracks_matcher.append_matcher(matcher2, or_match=False)
    
    assert matcher1 in tracks_matcher.matchers
    assert matcher2 in tracks_matcher.matchers

def test_append_matcher_with_or_match():
    matcher1 = MagicMock()
    matcher2 = MagicMock()
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.append_matcher(matcher1, or_match=False)
    assert matcher1 in tracks_matcher.matchers
    tracks_matcher.append_matcher(matcher2, or_match=True)
    assert isinstance(tracks_matcher.matchers[-1], _OrMetaMatcher)

def test_append_matcher_with_or_match_initial():
    matcher1 = MagicMock()
    matcher2 = MagicMock()
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.append_matcher(matcher1, or_match=True)
    assert matcher1 not in tracks_matcher.matchers
    tracks_matcher.append_matcher(matcher2, or_match=True)
    assert isinstance(tracks_matcher.matchers[-1], _OrMetaMatcher)

def test_prepend_matcher_without_or_match():
    matcher1 = MagicMock()
    matcher2 = MagicMock()
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.prepend_matcher(matcher1, or_match=False)
    assert matcher1 in tracks_matcher.matchers
    tracks_matcher.prepend_matcher(matcher2, or_match=False)
    assert matcher2, matcher1 in tracks_matcher.matchers
    
def test_prepend_matcher_with_or_match():
    matcher1 = MagicMock()
    matcher2 = MagicMock()
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.prepend_matcher(matcher1, or_match=False)
    assert matcher1 in tracks_matcher.matchers
    tracks_matcher.prepend_matcher(matcher2, or_match=True)
    assert isinstance(tracks_matcher.matchers[0], _OrMetaMatcher)

def test_prepend_matcher_with_or_match_initial():
    matcher1 = MagicMock()
    matcher2 = MagicMock()
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.prepend_matcher(matcher1, or_match=True)
    assert matcher1 not in tracks_matcher.matchers
    tracks_matcher.prepend_matcher(matcher2, or_match=True)
    assert isinstance(tracks_matcher.matchers[0], _OrMetaMatcher)

def test_match_all_matchers_true():
    mock_srtrack = SearchResultTrack(track=None)
    matcher1 = MagicMock(spec=_Matcher)
    matcher1.match.return_value = True
    matcher2 = MagicMock(spec=_Matcher)
    matcher2.match.return_value = True
    matcher3 = MagicMock(spec=_Matcher)
    matcher3.match.return_value = True
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.matchers = [matcher1, matcher2, matcher3]
    result = tracks_matcher.match(mock_srtrack)
    assert result == True

def test_match_one_matcher_false():
    mock_srtrack = SearchResultTrack(track=None)
    matcher1 = MagicMock(spec=_Matcher)
    matcher1.match.return_value = True
    matcher2 = MagicMock(spec=_Matcher)
    matcher2.match.return_value = False
    matcher3 = MagicMock(spec=_Matcher)
    matcher3.match.return_value = True
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.matchers = [matcher1, matcher2, matcher3]
    result = tracks_matcher.match(mock_srtrack)
    assert result == False

def test_match_no_matchers():
    mock_srtrack = SearchResultTrack(track=None)
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.matchers = []
    result = tracks_matcher.match(mock_srtrack)
    assert result == True

def test_match_with_tags():
    mock_srtrack = SearchResultTrack(track=None)
    matcher1 = MagicMock(spec=_Matcher)
    matcher1.match.return_value = True
    matcher1.tag = "tag1"
    matcher2 = MagicMock(spec=_Matcher)
    matcher2.match.return_value = True
    matcher2.tags = {"tag2", "tag3"}
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.matchers = [matcher1, matcher2]
    result = tracks_matcher.match(mock_srtrack)
    assert result == True

def test_match_with_existing_tags():
    mock_srtrack = SearchResultTrack(track=None)
    mock_srtrack.on_tags = ["existing_tag"]
    matcher1 = MagicMock(spec=_Matcher)
    matcher1.match.return_value = True
    matcher1.tag = "tag1"
    matcher2 = MagicMock(spec=_Matcher)
    matcher2.match.return_value = True
    matcher2.tags = {"tag2", "tag3"}
    tracks_matcher = TracksMatcher(search_string="track name: test Track1")
    tracks_matcher.matchers = [matcher1, matcher2]
    result = tracks_matcher.match(mock_srtrack)
    assert result == True
    # assert mock_srtrack.on_tags == ["existing_tag", "tag1", "tag2", "tag3"]


def test_tokens_to_matchers_exact_match():
    tokens = ["track==test"]
    matcher = TracksMatcher(search_string="track==test")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert isinstance(result[0], _ExactMatcher)

def test_tokens_to_matchers_keyword_match():
    tokens = ["track=test"]
    matcher = TracksMatcher(search_string="track=test")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert isinstance(result[0], _InMatcher)

def test_tokens_to_matchers_greater_than_match():
    tokens = ["track>test"]
    matcher = TracksMatcher(search_string="track>test")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert isinstance(result[0], _GtMatcher)

def test_tokens_to_matchers_less_than_match():
    tokens = ["track<test"]
    matcher = TracksMatcher(search_string="track<test")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert isinstance(result[0], _LtMatcher)

def test_tokens_to_matchers_regex_match():
    tokens = ["track~test"]
    matcher = TracksMatcher(search_string="track~test")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert isinstance(result[0], _RegexMatcher)

def test_tokens_to_matchers_keyword_tags():
    tokens = ["test"]
    matcher = TracksMatcher(search_string="test", keyword_tags=["track"])
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert isinstance(result[0], _ManyMultiMetaMatcher)

def test_tokens_to_matchers_or_match():
    tokens = ["|", ["track==test1", "track==test2"]]
    matcher = TracksMatcher(search_string="track==test1|track==test2")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert not isinstance(result[0], _OrMetaMatcher)

def test_tokens_to_matchers_not_match():
    tokens = ["!", ["track==test"]]
    matcher = TracksMatcher(search_string="!track==test")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert not isinstance(result[0], _NotMetaMatcher)

def test_tokens_to_matchers_multiple_conditions():
    tokens = ["track==test", "artist==test", "|", ["track==test1", "track==test2"], "!", ["track==test3"]]
    matcher = TracksMatcher(search_string="track==test artist==test | track==test1|track==test2 !track==test3")
    result = matcher._TracksMatcher__tokens_to_matchers(tokens)
    assert isinstance(result[0], _ExactMatcher)
    assert isinstance(result[1], _ExactMatcher)
    
def test_red_with_parentheses():
    tokens = ["a", "(", "b", ")", "c"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__red(tokens)
    assert result == ["a", ["(", ["b"]], "c"]

def test_red_with_not():
    tokens = ["a", "!", "b", "c"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__red(tokens)
    assert result == ["a", ["!", ["b"]], "c"]

def test_red_with_or():
    tokens = ["a", "b", "|", "c", "d"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__red(tokens)
    assert result == ["a", ["|", ["b", "c"]], "d"]

def test_red_multiple_operations():
    tokens = ["z", "b", "|", "c", "d"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__red(tokens)
    assert result ==["z", ["|", ["b", "c"]], "d"]

def test_tokenize_query_basic():
    search_string = "track==test artist==test"
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ["", "track==test", "artist==test"]

def test_tokenize_query_with_quotes():
    search_string = '"track name: test Track1"'
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ['', 'track name: test Track1']

def test_tokenize_query_with_special_characters():
    search_string = "track==test artist==test trackname==\"test~!|\""
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ['', "track==test", "artist==test", "trackname==test~!|"]

def test_tokenize_query_with_regex():
    search_string = "track~test"
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ['', "track~test"]

def test_tokenize_query_with_or():
    search_string = "track==test|artist==test"
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ['', "track==test|artist==test"]

def test_tokenize_query_with_not():
    search_string = "!track==test"
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ['', "!track==test"]

def test_tokenize_query_with_parentheses():
    search_string = "(track==test)"
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ['', "(track==test)",]

def test_tokenize_query_with_complex_expression():
    search_string = "(track==test|artist==test)!(trackname==\"test~!|\")"
    matcher = TracksMatcher(search_string=search_string)
    result = matcher._TracksMatcher__tokenize_query(search_string)
    assert result == ['', "(track==test|artist==test)!(trackname==test~!|)"]
    
def test_optimize_tokens_basic():
    tokens = ["a", "bb", "ccc"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["a", "bb", "ccc"]

def test_optimize_tokens_with_empty_list():
    tokens = []
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == []

def test_optimize_tokens_with_single_token():
    tokens = ["a"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["a"]

def test_optimize_tokens_with_longer_queries_first():
    tokens = ["aaa", "bb", "c"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["c", "bb", "aaa"]

def test_optimize_tokens_with_equal_length_queries():
    tokens = ["bbb", "aaa", "ccc"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["bbb", "aaa", "ccc"]

def test_optimize_tokens_with_single_token_2():
    tokens = ["a"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["a"]

def test_optimize_tokens_with_longer_queries_first_2():
    tokens = ["aaa", "bb", "aaa"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["bb", "aaa", "aaa"]

def test_optimize_tokens_with_equal_length_queries_2():
    tokens = ["zzzz", "aaaa", "bbbb"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["zzzz", "aaaa", "bbbb"]

def test_optimize_tokens_with_single_token_1():
    tokens = ["z"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["z"]

def test_optimize_tokens_with_longer_queries_first_1():
    tokens = ["iiii", "bb", "aaa"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["bb", "aaa", "iiii"]

def test_optimize_tokens_with_equal_length_queries_1():
    tokens = ["vvvv", "hhhh", "cccc"]
    matcher = TracksMatcher(search_string="")
    result = matcher._TracksMatcher__optimize_tokens(tokens)
    assert result == ["vvvv", "hhhh", "cccc"]

def test_tracks_in_list_with_list():
    track_list = ["track1", "track2", "track3"]
    matcher = TracksInList(tracks=track_list)
    track1 = MagicMock(spec=SearchResultTrack)
    track1.track = "track1"
    assert matcher.match(track1) == True
    track4 = MagicMock(spec=SearchResultTrack)
    track4.track = "track4"
    assert matcher.match(track4) == False

def test_tracks_in_list_with_set():
    track_set = {"track1", "track2", "track3"}
    matcher = TracksInList(tracks=track_set)
    track1 = MagicMock(spec=SearchResultTrack)
    track1.track = "track1"
    assert matcher.match(track1) == True
    track4 = MagicMock(spec=SearchResultTrack)
    track4.track = "track4"
    assert matcher.match(track4) == False

def test_tracks_in_list_with_dict():
    track_dict = {"track1": 1, "track2": 2, "track3": 3}
    matcher = TracksInList(tracks=track_dict)
    track1 = MagicMock(spec=SearchResultTrack)
    track1.track = "track1"
    assert matcher.match(track1) == True
    track4 = MagicMock(spec=SearchResultTrack)
    track4.track = "track4"
    assert matcher.match(track4) == False
    
def test_tracks_not_in_list_with_list():
    track_list = ["track1", "track2", "track3"]
    matcher = TracksNotInList(tracks=track_list)
    track1 = MagicMock(spec=SearchResultTrack)
    track1.track = "track1"
    assert matcher.match(track1) == False
    track4 = MagicMock(spec=SearchResultTrack)
    track4.track = "track4"
    assert matcher.match(track4) == True

def test_tracks_not_in_list_with_set():
    track_set = {"track1", "track2", "track3"}
    matcher = TracksNotInList(tracks=track_set)
    track1 = MagicMock(spec=SearchResultTrack)
    track1.track = "track1"
    assert matcher.match(track1) == False
    track4 = MagicMock(spec=SearchResultTrack)
    track4.track = "track4"
    assert matcher.match(track4) == True

def test_tracks_not_in_list_with_dict():
    track_dict = {"track1": 1, "track2": 2, "track3": 3}
    matcher = TracksNotInList(tracks=track_dict)
    track1 = MagicMock(spec=SearchResultTrack)
    track1.track = "track1"
    assert matcher.match(track1) == False
    track4 = MagicMock(spec=SearchResultTrack)
    track4.track = "track4"
    assert matcher.match(track4) == True

def test_search_tracks_with_empty_iterable():
    track_iter = []
    track_matchers = [MagicMock(spec=TracksMatcher)]
    result = list(search_tracks(track_iter, track_matchers))
    assert result == []

def test_search_tracks_with_single_matcher():
    track_iter = [MagicMock(spec=SearchResultTrack, track="track1")]
    track_matcher = MagicMock(spec=TracksMatcher)
    track_matcher.match.return_value = True
    result = list(search_tracks(track_iter, [track_matcher]))
    assert len(result) == 1
    assert result[0].track == "track1"

def test_search_tracks_with_multiple_matchers():
    track_iter = [
        MagicMock(spec=SearchResultTrack, track="track1"),
        MagicMock(spec=SearchResultTrack, track="track2"),
        MagicMock(spec=SearchResultTrack, track="track3")
    ]
    track_matcher1 = MagicMock(spec=TracksMatcher)
    track_matcher1.match.return_value = True
    track_matcher2 = MagicMock(spec=TracksMatcher)
    track_matcher2.match.return_value = False
    result = list(search_tracks(track_iter, [track_matcher1, track_matcher2]))
    assert len(result) == 0

def test_search_tracks_with_no_match():
    track_iter = [
        MagicMock(spec=SearchResultTrack, track="track1"),
        MagicMock(spec=SearchResultTrack, track="track2"),
        MagicMock(spec=SearchResultTrack, track="track3")
    ]
    track_matcher = MagicMock(spec=TracksMatcher)
    track_matcher.match.return_value = False
    result = list(search_tracks(track_iter, [track_matcher]))
    assert len(result) == 0
    

def test_search_tracks_from_string_with_empty_iterable():
    track_iter = []
    result = list(search_tracks_from_string(track_iter, "track==test"))
    assert result == []
    
@pytest.fixture
def mock_tracks_matcher():
    with patch('xl.trax.search.TracksMatcher') as mock_class:
        yield mock_class.return_value

def test_match_track_from_string_with_matching_track(mock_tracks_matcher):
    mock_tracks_matcher.match.return_value = True
    track = "example_track"
    search_string = "example_search_string"

    result = match_track_from_string(track, search_string)

    assert result == True

def test_match_track_from_string_with_non_matching_track(mock_tracks_matcher):
    mock_tracks_matcher.match.return_value = False
    track = "example_track"
    search_string = "example_search_string"

    result = match_track_from_string(track, search_string)

    assert result == False

def test_search_tracks_from_string_with_matching_track(mock_tracks_matcher):
    mock_search_tracks = MagicMock()
    mock_tracks_matcher_instance = MagicMock()
    mock_tracks_matcher.return_value = mock_tracks_matcher_instance
    trackiter = ["track1", "track2", "track3"]
    search_string = "example_search_string"

    result = search_tracks_from_string(trackiter, search_string)
    assert isinstance(result, types.GeneratorType)
    
def test_search_tracks_from_string_with_custom_options(mock_tracks_matcher):
    mock_search_tracks = MagicMock()
    mock_tracks_matcher_instance = MagicMock()
    mock_tracks_matcher.return_value = mock_tracks_matcher_instance
    trackiter = ["track1", "track2", "track3"]
    search_string = "example_search_string"
    case_sensitive = False
    keyword_tags = ["tag1", "tag2"]

    result = search_tracks_from_string(trackiter, search_string, case_sensitive, keyword_tags)

    assert isinstance(result, types.GeneratorType)
    
