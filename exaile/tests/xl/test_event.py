import pytest
import weakref
import types
import gc
from unittest.mock import MagicMock, ANY, call, patch
from xl.event import log_event, add_callback, add_ui_callback, remove_callback, EVENT_MANAGER, Event, Callback, _WeakMethod, _NONE, EventManager

@pytest.fixture
def event_manager_mock(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("xl.event.EVENT_MANAGER", mock)
    return mock

def test_log_event(event_manager_mock):
    log_event('test_event', 'sender_object', 'event_data')
    assert event_manager_mock.emit.called
    event_arg = event_manager_mock.emit.call_args[0][0]
    assert isinstance(event_arg, Event)
    assert hasattr(event_arg, 'type') and event_arg.type == 'test_event'
    assert hasattr(event_arg, 'object') and event_arg.object == 'sender_object'
    assert hasattr(event_arg, 'data') and event_arg.data == 'event_data'

def test_add_callback(event_manager_mock):
    callback = lambda x: x
    add_callback(callback, 'event_type', 'event_object')
    event_manager_mock.add_callback.assert_called_once_with(
        callback, 'event_type', 'event_object', (), {}
    )

def test_add_ui_callback(event_manager_mock):
    callback = lambda x: x
    add_ui_callback(callback, 'ui_event_type', 'ui_event_object')
    event_manager_mock.add_callback.assert_called_once_with(
        callback, 'ui_event_type', 'ui_event_object', (), {}, ui=True
    )

def test_remove_callback(event_manager_mock):
    callback = lambda x: x
    remove_callback(callback, 'event_type', 'event_object')
    event_manager_mock.remove_callback.assert_called_once_with(
        callback, 'event_type', 'event_object'
    )

def _getWeakRef(func):
    return weakref.ref(func)

def test_callback_init():
    def test_func():
        return "Testing"
    args = (1, 2)
    kwargs = {'a': 3, 'b': 4}
    callback_time = 1234567890
    callback = Callback(test_func, callback_time, args, kwargs)
    assert callback.wfunction() is test_func
    assert callback.time == callback_time
    assert callback.args == args
    assert callback.kwargs == kwargs

def test_callback_repr():
    def test_func():
        return "Testing"
    callback_time = 1234567890
    callback = Callback(test_func, callback_time, (), {})
    func_repr = repr(callback.wfunction())
    expected_repr = f"<Callback {func_repr}>"
    assert repr(callback) == expected_repr

def test_callback_weakref():
    def test_func():
        return "Testing"
    callback = Callback(test_func, 1234567890, (), {})
    del test_func
    assert callback.wfunction() is None

class SomeClass:
    def __init__(self, value):
        self.value = value

    def method(self):
        return self.value

def test_weakMethod_init_call():
    obj = SomeClass(10)
    method = obj.method
    weak_method = _WeakMethod(method)
    assert weak_method()() == 10

def test_weakMethod_equality():
    obj1 = SomeClass(10)
    obj2 = SomeClass(20)
    weak_method1 = _WeakMethod(obj1.method)
    weak_method2 = _WeakMethod(obj1.method)
    weak_method3 = _WeakMethod(obj2.method)
    assert weak_method1 == weak_method2
    assert weak_method1 != weak_method3

def test_weakMethod_hash():
    obj = SomeClass(10)
    weak_method = _WeakMethod(obj.method)
    assert hash(weak_method) == hash(obj.method.__func__)

def test_weakMethod_repr():
    obj = SomeClass(10)
    weak_method = _WeakMethod(obj.method)
    assert '; DEAD' not in repr(weak_method)
    del obj
    assert '; DEAD' in repr(weak_method)

def test_weakMethod_refs():
    obj = SomeClass(10)
    method = obj.method
    weak_method = _WeakMethod(method)
    obj_ref = weakref.ref(obj)
    assert weak_method.refs(obj_ref)

@pytest.fixture
def event_manager():
    return EventManager(use_logger=True, logger_filter='test', verbose=True)

class TestObject:
    pass

def test_add_remove_callback(event_manager):
    callback = MagicMock()
    evty = 'test_event'
    obj = TestObject()
    remove = event_manager.add_callback(callback, evty, obj, (), {})
    assert evty in event_manager.callbacks
    assert obj in event_manager.callbacks[evty]
    assert event_manager.callbacks[evty][obj][0].wfunction() == callback
    remove()
    assert evty not in event_manager.callbacks or obj not in event_manager.callbacks[evty]

def test_emit(event_manager):
    event = Event('test_event', TestObject(), 'test_data')
    callback = MagicMock()
    event_manager.add_callback(callback, event.type, event.object, (), {})
    event_manager.emit(event)
    callback.assert_called_once_with(event.type, event.object, event.data)

def test_emit_async(event_manager):
    event = Event('test_event', TestObject(), 'test_data')
    callback = MagicMock()
    event_manager.add_callback(callback, event.type, event.object, (), {})
    with patch('xl.event.GLib.idle_add', side_effect=lambda f, *args, **kwargs: f(*args, **kwargs)):
        event_manager.emit_async(event)
    callback.assert_called_once_with(event.type, event.object, event.data)

def test_emit_no_callbacks(event_manager):
    event = Event('test_event', 'test_object', 'test_data')
    event_manager.emit(event)
