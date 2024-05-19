import pytest
import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from xl.nls import gettext as _
import logging
import xl.transcoder
from unittest.mock import MagicMock
from xl.transcoder import get_formats, add_format, Transcoder, TranscodeError

def test_get_formats():
    assert isinstance(get_formats(), dict)

def test_add_format():
    transcoder = Transcoder(destformat='Ogg Vorbis', quality=0.5, error_callback=None, end_callback=None)
    with pytest.raises(AttributeError):
        transcoder.add_format('AAC', {})

def test_transcoder_init():
    def error_callback(error, message):
        pass
    def end_callback():
        pass
    transcoder = Transcoder("Ogg Vorbis", 0.5, error_callback, end_callback)
    assert transcoder.dest_format == "Ogg Vorbis"
    assert transcoder.quality == 0.5
    assert transcoder.input is None
    assert transcoder.output is None
    assert not transcoder.running

def test_transcoder_set_format():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder.set_format("FLAC")
    assert transcoder.dest_format == "FLAC"

def test_transcoder_set_quality():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder.set_quality(0.6)
    assert transcoder.quality == 0.6

def test_construct_encoder():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder._construct_encoder()
    assert transcoder.encoder == "vorbisenc quality=0.5 ! oggmux"

def test_set_input():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder.set_input("input_file.mp3")
    assert transcoder.input == """filesrc location="input_file.mp3" """

def test_set_raw_input():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder.set_raw_input("input_source")
    assert transcoder.input == "input_source"

def test_set_output():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder.set_output("output_file.ogg")
    assert transcoder.output == """filesink location="output_file.ogg" """

def test_set_output_raw():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder.set_output_raw("output_sink")
    assert transcoder.output == "output_sink"

def test_start_transcode():
    Gst.init(None)
    transcoder = Transcoder(destformat='Ogg Vorbis', quality=0.5, error_callback=None, end_callback=None)
    transcoder.set_input('input_uri')
    transcoder.set_output('output_uri')
    assert transcoder.start_transcode() is not None

def test_stop():
    Gst.init(None)
    transcoder = Transcoder(destformat='Ogg Vorbis', quality=0.5, error_callback=None, end_callback=None)
    with pytest.raises(AttributeError):
        transcoder.stop()

def test_on_error():
    Gst.init(None)
    transcoder = Transcoder(destformat='Ogg Vorbis', quality=0.5, error_callback=None, end_callback=None)
    bus = MagicMock()
    message = MagicMock()
    with pytest.raises(AttributeError):
        transcoder.on_error(bus, message)

def test_on_eof(mocker):
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    mock_pipe = MagicMock()
    transcoder.pipe = mock_pipe
    transcoder.stop = MagicMock()
    transcoder.on_eof(None, None)
    transcoder.stop.assert_called_once()

def test_get_time():
    transcoder = Transcoder(destformat='Ogg Vorbis', quality=0.5, error_callback=None, end_callback=None)
    assert transcoder.get_time() == 0.0

def test_is_running():
    transcoder = Transcoder("Ogg Vorbis", 0.5, None, None)
    transcoder.running = True
    assert transcoder.is_running() == True
