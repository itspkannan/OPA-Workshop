from sanic.exceptions import Forbidden

from simple_opa_integration.container import Container
from simple_opa_integration.services.authorization_service import AuthorizationService


def register_auth_middleware():
    async def auth_middleware(request):
        auth_service = Container.resolve(AuthorizationService)
        user_role = request.headers.get("x-role", "guest")
        allowed = await auth_service.is_allowed(user_role, request.method, request.path)
        if not allowed:
            raise Forbidden("Access Denied")
    return auth_middleware