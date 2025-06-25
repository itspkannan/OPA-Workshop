from functools import partial

from sanic import Sanic
from sanic.worker.loader import AppLoader

from simple_opa_integration.config.auth_config import AuthConfig
from simple_opa_integration.config.server_config import ServerConfig
from simple_opa_integration.container import Container
from simple_opa_integration.middleware.authz_middleware import register_auth_middleware
from simple_opa_integration.routes.routes import register_routes
from simple_opa_integration.services.authorization_service import AuthorizationService
from simple_opa_integration.services.configuration_service import ConfigurationService
from simple_opa_integration.services.user_service import UserService


def __bootstrap(config_dir: str):
    config_service = ConfigurationService()
    Container.register(ConfigurationService, lambda: config_service)
    auth_config = config_service.load(f'{config_dir}/auth_config.yaml', AuthConfig, 'authorization')
    Container.register(AuthorizationService, lambda: AuthorizationService(auth_config))
    user_service = UserService()
    Container.register(UserService, lambda: user_service)
    print(Container.resolve(UserService))

def __create_app(config_dir: str, app_name: str):
    __bootstrap(config_dir)
    app = Sanic(app_name)
    middleware_fn = register_auth_middleware()
    app.register_middleware(middleware_fn, attach_to="request")
    register_routes(app)
    return app

def startup(config_dir: str, app_name: str = 'OPAWithSanic'):
    loader = AppLoader(factory=partial(__create_app, config_dir, app_name))
    app = loader.load()

    config_service = Container.resolve(ConfigurationService)
    server_config = config_service.load(f'{config_dir}/server_config.yaml', ServerConfig, 'server')

    app.prepare(
        host=server_config.host,
        port=server_config.port,
        workers=server_config.workers,
        dev=server_config.dev,
        access_log=server_config.access_log
    )
    Sanic.serve(primary=app, app_loader=loader)
