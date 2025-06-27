import uuid

from sanic import Request, HTTPResponse, json

from restapi_auth_opa_integration.container import Container
from restapi_auth_opa_integration.services.user_service import UserService
from uuid import UUID

class UserController:
    def __init__(self):
        self.user_service = Container.resolve(UserService)

    async def get(self, request: Request) -> HTTPResponse:
        users = self.user_service.get_all()
        return json([{"id": uid, "name": name} for uid, name in users])

    async def create(self, request: Request) -> HTTPResponse:
        data = request.json
        self.user_service.create(str(uuid.uuid4()),data["name"])
        return json({"status": "created"}, status=201)

    async def update(self, request: Request, user_id: UUID) -> HTTPResponse:
        data = request.json
        self.user_service.update(user_id, data["name"])
        return json({"status": "updated"})

    async def delete(self, request: Request, user_id: UUID) -> HTTPResponse:
        self.user_service.delete(user_id)
        return json({"status": "deleted"})
