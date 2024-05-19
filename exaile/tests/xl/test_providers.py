import pytest
import logging
from xl import event
from unittest.mock import patch, MagicMock, mock_open
from xl.providers import ProviderManager, ProviderHandler, MultiProviderHandler, event


@pytest.fixture
def manager():
    return ProviderManager()

@pytest.fixture(autouse=True)
def mock_event(mocker):
    mocker.patch('xl.providers.event.add_ui_callback')

@pytest.fixture
def provider_handler(manager):
    return ProviderHandler(servicename="test_service", target="some_target", simple_init=False)

def test_init(manager):
    assert isinstance(manager.services, dict)
    assert len(manager.services) == 0

def test_register_provider(manager):
    class MockProvider:
        name = "MockProvider"
    provider = MockProvider()
    manager.register_provider("test_service", provider)
    assert "test_service" in manager.services
    assert provider in manager.services["test_service"][None]

def test_unregister_provider(manager):
    class MockProvider:
        name = "MockProvider"
    provider = MockProvider()
    manager.register_provider("test_service", provider)
    manager.unregister_provider("test_service", provider)
    if None in manager.services["test_service"]:
        assert not manager.services["test_service"][None]
    else:
        assert None not in manager.services["test_service"]

def test_manager_get_providers(manager):
    class MockProvider:
        name = "MockProvider"
    provider = MockProvider()
    manager.register_provider("test_service", provider, None)
    assert provider in manager.get_providers("test_service", None)

def test_manager_get_provider(manager):
    class MockProvider:
        name = "MockProvider"
    provider = MockProvider()
    manager.register_provider("test_service", provider, None)
    fetched_provider = manager.get_provider("test_service", "MockProvider", None)
    assert fetched_provider == provider

def test_provider_handler_init(provider_handler):
    assert provider_handler.servicename == "test_service"
    assert provider_handler.target == "some_target"

def test_add_callback(provider_handler):
    class MockProvider:
        name = "MockProvider"
    provider = MockProvider()
    provider_handler._add_callback("test_service", None, (provider, provider_handler.target))

def test_remove_callback(provider_handler):
    class MockProvider:
        name = "MockProvider"
    provider = MockProvider()
    provider_handler._remove_callback("test_service", None, (provider, provider_handler.target))

class MockProvider:
    def __init__(self, name):
        self.name = name

@pytest.fixture
def multi_provider_handler():
    servicenames = ["service1", "service2"]
    return MultiProviderHandler(servicenames, target="some_target", simple_init=True)

def test_multi_provider_handler_init(multi_provider_handler):
    assert len(multi_provider_handler.providers) == 2
    for proxy in multi_provider_handler.providers:
        assert isinstance(proxy, MultiProviderHandler._ProxyProvider)

def test_on_provider_added(multi_provider_handler, mocker):
    mock_provider = MockProvider("TestProvider")
    spy = mocker.spy(multi_provider_handler, 'on_provider_added')
    multi_provider_handler.providers[0].on_provider_added(mock_provider)
    spy.assert_called_once_with(mock_provider)

def test_on_provider_removed(multi_provider_handler, mocker):
    mock_provider = MockProvider("TestProvider")
    spy = mocker.spy(multi_provider_handler, 'on_provider_removed')
    multi_provider_handler.providers[0].on_provider_removed(mock_provider)
    spy.assert_called_once_with(mock_provider)

def test_get_providers(multi_provider_handler, mocker):
    mocker.patch.object(ProviderHandler, 'get_providers', return_value=[MockProvider("Provider1"), MockProvider("Provider2")])    
    providers = multi_provider_handler.get_providers()
    assert len(providers) == 4
    assert {p.name for p in providers} == {"Provider1", "Provider2"}

def test_no_service_names():
    multi_provider_handler = MultiProviderHandler([])
    assert len(multi_provider_handler.providers) == 0


