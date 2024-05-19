import pytest
from unittest.mock import patch, MagicMock
from xl.common import get_url_contents, clamp, enum, sanitize_url, LimitedCache, TimeSpan
import urllib.request


def test_clamp_in_range():
    assert clamp(5, 1, 10) == 5

def test_clamp_minimum():
    assert clamp(0, 1, 10) == 1

def test_clamp_maximum():
    assert clamp(15, 1, 10) == 10

def test_enum():
    Colors = enum(RED=1, GREEN=2, BLUE=3)
    assert Colors.RED == 1
    assert Colors.GREEN == 2
    assert Colors.BLUE == 3

def test_sanitize_url():
    url = "http://username:password@exaile.org/path"
    assert sanitize_url(url) == "http://username:*****@exaile.org/path"

@patch('xl.common.urllib.request.urlopen')
def test_get_url_contents(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b"value"
    mock_urlopen.return_value = mock_response
    
    result = get_url_contents("http://exaile.org", "TestAgent")
    assert result == b"value"
    assert mock_urlopen.call_count == 1
    called_args, called_kwargs = mock_urlopen.call_args
    request_object = called_args[0]
    assert isinstance(request_object, urllib.request.Request)  
    assert request_object.full_url == "http://exaile.org"
    assert 'user-agent' in (key.lower() for key in request_object.headers)
    assert request_object.headers.get('User-agent') == "TestAgent"

def test_initlen():
    limit = 5
    cache = LimitedCache(limit)
    assert len(cache) == 0
    assert cache.limit == limit

def test_setitem():
    cache = LimitedCache(2)
    cache['a'] = 1
    cache['b'] = 2
    cache['c'] = 3
    assert 'a' not in cache
    assert len(cache) == 2
    assert cache['b'] == 2 and cache['c'] == 3

def test_getitem():
    cache = LimitedCache(2)
    cache['a'] = 1
    cache['b'] = 2
    assert cache['a'] == 1
    _ = cache['a']
    cache['c'] = 3   
    assert 'b' not in cache
    assert cache['a'] == 1

def test_delitem():
    cache = LimitedCache(3)
    cache['a'] = 1
    cache['b'] = 2
    del cache['a']
    assert 'a' not in cache
    assert len(cache) == 1

def test_contains():
    cache = LimitedCache(2)
    cache['a'] = 1
    cache['b'] = 2   
    assert 'a' in cache
    assert 'c' not in cache

def test_iter_keys():
    cache = LimitedCache(2)
    cache['a'] = 1
    cache['b'] = 2
    keys = list(iter(cache))
    assert keys == ['a', 'b']
    keys_method = list(cache.keys())
    assert keys_method == keys

def test_repr_str():
    cache = LimitedCache(2)
    cache['a'] = 1
    cache['b'] = 2    
    rep = repr(cache)
    str_rep = str(cache)    
    assert rep == "{'a': 1, 'b': 2}"
    assert str_rep == "{'a': 1, 'b': 2}"

def test_initTimeSpan():
    # 1 day, 2 hours, 3 minutes and 10 seconds
    span_seconds = 93790
    timespan = TimeSpan(span_seconds)
    assert timespan.days == 1
    assert timespan.hours == 2
    assert timespan.minutes == 3
    assert timespan.seconds == 10

    # zero seconds
    timespan = TimeSpan(0)
    assert timespan.days == 0
    assert timespan.hours == 0
    assert timespan.minutes == 0
    assert timespan.seconds == 0

    # one day
    timespan = TimeSpan(86400)
    assert timespan.days == 1
    assert timespan.hours == 0
    assert timespan.minutes == 0
    assert timespan.seconds == 0

    # 1.5 day
    timespan = TimeSpan(129600)
    assert timespan.days == 1
    assert timespan.hours == 12
    assert timespan.minutes == 0
    assert timespan.seconds == 0

def test_various_cases():
    # string
    with pytest.raises(ValueError):
        TimeSpan("string")

    # None
    with pytest.raises(ValueError):
        TimeSpan(None)

    # negative values
    with pytest.raises(ValueError):
        TimeSpan(-500)

    # large numbers
    timespan = TimeSpan(9615236480)
    days = 9615236480 / 86400
    assert timespan.days == int(days)


def test_str_repr():
    timespan = TimeSpan(93790)
    assert str(timespan) == "1d, 2h, 3m, 10s"
    assert repr(timespan) == "TimeSpan(93790.0)"

