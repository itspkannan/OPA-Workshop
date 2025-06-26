package simple.authz
import data.common.utils.is_valid_uuid
import data.common.utils.jwt.decode_token

default allow = false

allow if{
    payload := decode_token(input.token)
    payload.role == "admin"
    input.method == "GET"
    input.path = ["api", "v1", "users"]
}

allow if {
    payload := decode_token(input.token)
    payload.role in ["admin", "viewer"]
    input.method == "GET"
    input.path = ["api", "v1", "users", user_id]
    is_valid_uuid(user_id)
}

allow if{
    payload := decode_token(input.token)
    payload.role == "admin"
    input.method == "POST"
    input.path = ["api", "v1", "users"]
}

allow if{
    payload := decode_token(input.token)
    payload.role == "admin"
    input.method == "PUT"
    input.path = ["api", "v1", "users", user_id]
    is_valid_uuid(user_id)
}

allow if{
    payload := decode_token(input.token)
    payload.role == "admin"
    input.method == "DELETE"
    input.path = ["api", "v1", "users", user_id]
    is_valid_uuid(user_id)
}
