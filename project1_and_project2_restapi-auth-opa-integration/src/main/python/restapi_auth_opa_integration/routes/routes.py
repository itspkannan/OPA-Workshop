from sanic import Blueprint, Sanic
from restapi_auth_opa_integration.controllers import UserController, HealthCheckController

from sanic import json

def register_routes(app: Sanic):
    health_controller = HealthCheckController()
    health_check_bp = Blueprint("healthcheck")
    health_check_bp.add_route(health_controller.get, "/health", methods=["GET"])

    user_controller = UserController()
    users_bp = Blueprint("users", url_prefix="/api/v1")
    users_bp.add_route(user_controller.get, "/users", methods=["GET"])
    users_bp.add_route(user_controller.create, "/users", methods=["POST"])
    users_bp.add_route(user_controller.update, "/users/<user_id:uuid>", methods=["PUT"])
    users_bp.add_route(user_controller.delete, "/users/<user_id:uuid>", methods=["DELETE"])
    app.blueprint(health_check_bp)
    app.blueprint(users_bp)
