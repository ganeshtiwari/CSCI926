import os
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from xl.version import get_current_version, get_current_revision

@pytest.fixture(autouse=True)
def set_exaile_dirEnvVariable(tmpdir, monkeypatch):
    exaile_dir = str(tmpdir)
    monkeypatch.setenv("EXAILE_DIR", exaile_dir)

def test_get_current_version_nogit(tmpdir):
    with patch('subprocess.check_output', MagicMock(side_effect=subprocess.CalledProcessError(128, 'cmd'))):
        assert get_current_version() is None

def test_get_current_revision_nogit(tmpdir):
    with patch('subprocess.check_output', MagicMock(side_effect=subprocess.CalledProcessError(128, 'cmd'))):
        assert get_current_revision() is None

def test_get_current_version_success(tmpdir):
    with patch('subprocess.check_output', MagicMock(return_value=b'1.0')):
        assert get_current_version() == '1.0'

def test_get_current_revision_success(tmpdir):
    with patch('subprocess.check_output', MagicMock(return_value=b'abc123')):
        assert get_current_revision() == 'abc123'

def test_get_current_version_error(tmpdir):
    with patch('subprocess.check_output', MagicMock(side_effect=subprocess.CalledProcessError(1, 'cmd'))):
        assert get_current_version() is None

def test_get_current_revision_error(tmpdir):
    with patch('subprocess.check_output', MagicMock(side_effect=subprocess.CalledProcessError(1, 'cmd'))):
        assert get_current_revision() is None