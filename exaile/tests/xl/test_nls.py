import locale
import os
import os.path
import sys
from typing import Optional
from xl.nls import _get_locale_path, _setup_locale, gettext, ngettext


def test_gettext():
    global gettextmod
    gettextmod = True
    assert gettext('Test') == 'Test'
    gettextmod = False
    assert gettext('Test') == 'Test'

def test_ngettext():
    global gettextmod
    gettextmod = True
    assert ngettext('apple', 'apples', 1) == 'apple'
    assert ngettext('apple', 'apples', 2) == 'apples'
    gettextmod = False
    assert ngettext('apple', 'apples', 1) == 'apple'
    assert ngettext('apple', 'apples', 2) == 'apples'
