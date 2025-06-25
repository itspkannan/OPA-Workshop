from sanic import Blueprint, Sanic
from simple_opa_integration.controllers.user_controller import UserController


def register_routes(app: Sanic):
    user_controller = UserController()
    users_bp = Blueprint("users", url_prefix="/api/v1")
    users_bp.add_route(user_controller.get, "/users", methods=["GET"])
    users_bp.add_route(user_controller.create, "/users", methods=["POST"])
    users_bp.add_route(user_controller.update, "/users/<user_id:int>", methods=["PUT"])
    users_bp.add_route(user_controller.delete, "/users/<user_id:int>", methods=["DELETE"])
    app.blueprint(users_bp)
