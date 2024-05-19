import pytest
import logging
import logging.handlers
from pprint import PrettyPrinter
import os
import os.path
import sys
from unittest.mock import patch, MagicMock, call
from xl.logger_setup import FilterLogger, SafePrettyPrinter, VerboseExceptionFormatter, MAX_VARS_LINES, MAX_LINE_LENGTH, start_logging, stop_logging

def test_filterlogger_noModule_noLevel():
    logger = FilterLogger('test_logger')
    record = logging.LogRecord('test_logger', logging.INFO, '', 0, 'test message', [], None)
    assert logger.filter(record) == True

def test_filterlogger_module():
    FilterLogger.module = 'test_logger'
    FilterLogger.level = logging.NOTSET
    logger = FilterLogger('test_logger')
    correct_record = logging.LogRecord('test_logger', logging.INFO, '', 0, 'test message', [], None)
    incorrect_record = logging.LogRecord('wrong_logger', logging.INFO, '', 0, 'test message', [], None)
    assert logger.filter(correct_record) == True
    assert logger.filter(incorrect_record) == False

def test_filterlogger_level():
    FilterLogger.module = None
    FilterLogger.level = logging.INFO
    logger = FilterLogger('test_logger')
    correct_record = logging.LogRecord('test_logger', logging.INFO, '', 0, 'test message', [], None)
    incorrect_record = logging.LogRecord('test_logger', logging.DEBUG, '', 0, 'test message', [], None)
    assert logger.filter(correct_record) == True
    assert logger.filter(incorrect_record) == False

def test_filterlogger_module_level():
    FilterLogger.module = 'test_logger'
    FilterLogger.level = logging.INFO
    logger = FilterLogger('test_logger')
    correct_record = logging.LogRecord('test_logger', logging.INFO, '', 0, 'test message', [], None)
    incorrect_record_module = logging.LogRecord('wrong_logger', logging.INFO, '', 0, 'test message', [], None)
    incorrect_record_level = logging.LogRecord('test_logger', logging.DEBUG, '', 0, 'test message', [], None)
    assert logger.filter(correct_record) == True
    assert logger.filter(incorrect_record_module) == False
    assert logger.filter(incorrect_record_level) == False

def test_safePrettyPrinter_object():
    spp = SafePrettyPrinter()
    normal_object = {'key': 'value'}
    result = spp.pformat(normal_object)
    expected = "{'key': 'value'}"
    assert result == expected

def test_safePrettyPrinter_problem():
    class Problematic:
        def __repr__(self):
            raise Exception("error")
    spp = SafePrettyPrinter()
    problematic_object = Problematic()
    result = spp.pformat(problematic_object)
    assert "!! Cannot format: error" in result

def test_safePrettyPrinter_noProblem():
    spp = SafePrettyPrinter()
    simple_string = "test string"
    result = spp.pformat(simple_string)
    expected = "'test string'"
    assert result == expected

def test_safePrettyPrinter_numeric():
    spp = SafePrettyPrinter()
    number = 123
    result = spp.pformat(number)
    expected = '123'
    assert result == expected

def test_verboseExceptionFormatter_noLocals():
    formatter = VerboseExceptionFormatter(log_locals_on_exception=False)
    try:
        raise ValueError("Test error")
    except ValueError:
        formatted_exc = formatter.formatException(sys.exc_info())
    assert 'Locals at innermost frame:' not in formatted_exc

def test_verboseExceptionFormatter_locals():
    formatter = VerboseExceptionFormatter(log_locals_on_exception=True)
    try:
        local_var = "test"
        raise ValueError("Test error")
    except ValueError:
        formatted_exc = formatter.formatException(sys.exc_info())
    assert 'Locals at innermost frame:' in formatted_exc
    assert 'local_var' in formatted_exc

def test_verboseExceptionFormatter_maxLines():
    formatter = VerboseExceptionFormatter(log_locals_on_exception=True)
    try:
        locals_dict = {f'var{i}': f'value{i}' for i in range(50)}
        raise ValueError("Test error")
    except ValueError:
        formatted_exc = formatter.formatException(sys.exc_info())
    start_index = formatted_exc.find('Locals at innermost frame:') + len('Locals at innermost frame:')
    locals_text = formatted_exc[start_index:]
    locals_lines = locals_text.split('\n')[1:]
    locals_lines = [line for line in locals_lines if line.strip()]    
    assert len(locals_lines) <= MAX_VARS_LINES


def test_verboseExceptionFormatter_maxLineLength():
    formatter = VerboseExceptionFormatter(log_locals_on_exception=True)
    try:
        long_var = 'x' * 200
        raise ValueError("Test error")
    except ValueError:
        formatted_exc = formatter.formatException(sys.exc_info())
    locals_start = formatted_exc.find('Locals at innermost frame:')
    locals_text = formatted_exc[locals_start:] if locals_start != -1 else ""
    for line in locals_text.split('\n'):
        if line.strip():
            assert len(line) <= MAX_LINE_LENGTH or (line.endswith('...') and len(line) == MAX_LINE_LENGTH)

def test_start_logging_debug():
    with patch('logging.getLogger', return_value=MagicMock()) as mock_get_logger:
        mock_logger = mock_get_logger.return_value
        mock_logger.level = logging.NOTSET
        start_logging(debug=True, quiet=False, debugthreads=False, module_filter=None, level_filter=None)
        assert logging.root.level == logging.DEBUG
        assert mock_logger.setLevel.called_with(logging.DEBUG)

def test_start_logging_quiet():
    with patch('logging.StreamHandler') as mock_handler:
        mock_handler_instance = MagicMock()
        mock_handler.return_value = mock_handler_instance
        start_logging(debug=False, quiet=True, debugthreads=False, module_filter=None, level_filter=None)
        assert logging.root.level == logging.WARNING

def test_start_logging_module_level_filter():
    with patch('logging.setLoggerClass') as mock_set_logger_class:
        start_logging(debug=False, quiet=False, debugthreads=False, module_filter='test_module', level_filter='DEBUG')
        mock_set_logger_class.assert_called_once()

def test_formatter_debug():
    with patch('logging.StreamHandler.setFormatter') as mock_set_formatter:
        start_logging(debug=True, quiet=False, debugthreads=False, module_filter=None, level_filter=None)
        args_debug, _ = mock_set_formatter.call_args
        assert isinstance(args_debug[0], VerboseExceptionFormatter)
        start_logging(debug=False, quiet=False, debugthreads=False, module_filter=None, level_filter=None)
        args_nodebug, _ = mock_set_formatter.call_args
        assert isinstance(args_nodebug[0], logging.Formatter)

def test_logging_setup_rotation():
    with patch('logging.handlers.RotatingFileHandler') as mock_handler:
        start_logging(debug=False, quiet=False, debugthreads=False, module_filter=None, level_filter=None)
        mock_handler.assert_called_once()
        handler_args, handler_kwargs = mock_handler.call_args
        assert handler_kwargs['backupCount'] == 5
        handler_instance = mock_handler.return_value
        handler_instance.doRollover.assert_called_once()

def test_exception_excepthook():
    with patch('sys.excepthook') as mock_excepthook:
        start_logging(debug=True, quiet=False, debugthreads=False, module_filter=None, level_filter=None)
        assert mock_excepthook is not sys.excepthook

def test_signal_faulthandler_setup():
    import faulthandler
    with patch('faulthandler.register') as mock_register, \
         patch('faulthandler.enable') as mock_enable, \
         patch('sys.stderr.isatty', return_value=True) as mock_isatty:
        start_logging(debug=True, quiet=False, debugthreads=False, module_filter=None, level_filter=None)
        mock_enable.assert_called_once()
        if hasattr(faulthandler, 'register'):
            import signal
            mock_register.assert_called_with(signal.SIGUSR2)

def test_stop_logging():
    with patch('logging.shutdown') as mock_shutdown:
        stop_logging()
        mock_shutdown.assert_called_once()
