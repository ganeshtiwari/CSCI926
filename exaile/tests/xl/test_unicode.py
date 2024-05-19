import pytest
import unicodedata
from xl.unicode import shave_marks, to_unicode

def test_shave_marks_empty_string():
    assert shave_marks('') == ''

def test_shave_marks_no_marks():
    assert shave_marks('test1') == 'test1'

def test_shave_marks_marks():
    assert shave_marks('test2') == 'test2'

def test_shave_marks_combinedCharacters():
    assert shave_marks('test2') == 'test2'

def test_shave_marks_non_ascii():
    assert shave_marks('test3') == 'test3'

def test_to_unicode_string():
    assert to_unicode('test1') == 'test1'

def test_to_unicode_bytes():
    assert to_unicode(b'test1') == 'test1'

def test_to_unicode_non_string_bytes():
    assert to_unicode(123) == '123'

def test_to_unicode_encoding():
    assert to_unicode(b'\xc3\xa9', encoding='utf-8') == 'é'

def test_to_unicode_errors():
    with pytest.raises(UnicodeDecodeError):
        to_unicode(b'\xc3', encoding='utf-8', errors='strict')

    assert to_unicode(b'\xc3', encoding='utf-8', errors='ignore') == ''

    assert to_unicode(b'\xc3', encoding='utf-8', errors='replace') == '\ufffd'
