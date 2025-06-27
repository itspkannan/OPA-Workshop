import pytest
from sanic import Sanic
from simple_opa_integration.container import Container
from simple_opa_integration.services.authorization_service import AuthorizationService
from simple_opa_integration.services.user_service import UserService
from simple_opa_integration.services.configuration_service import ConfigurationService
from simple_opa_integration.routes.routes import register_routes


@pytest.fixture(autouse=True)
def reset_container():
    Container._registry = {}


@pytest.fixture
def mock_user_service(mocker):
    mock = mocker.Mock(spec=UserService)
    Container.register(UserService, lambda: mock)
    return mock


@pytest.fixture
def mock_authorization_service(mocker):
    mock_instance = mocker.Mock(spec=AuthorizationService)
    mock_instance.is_allowed = mocker.AsyncMock(return_value=True)
    Container.register(AuthorizationService, lambda config=None: mock_instance)

    return mock_instance


@pytest.fixture
def mock_config_service(mocker):
    mock = mocker.Mock(spec=ConfigurationService)
    mock.load.return_value = mocker.Mock()
    Container.register(ConfigurationService, lambda: mock)
    return mock


@pytest.fixture
def test_app(mock_user_service, mock_authorization_service, mock_config_service):
    app = Sanic("test-app")
    register_routes(app)
    return app
