from sanic.exceptions import Forbidden

from restapi_auth_opa_integration.container import Container
from restapi_auth_opa_integration.services.authorization_service import AuthorizationService


def register_auth_middleware():
    async def auth_middleware(request):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        auth_service = Container.resolve(AuthorizationService)
        response = await auth_service.is_allowed(token, request.method, request.path)
        if not response.get('allow', False):
            raise Forbidden("Access Denied")
    return auth_middleware