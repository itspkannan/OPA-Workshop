package simple.authz
import data.common.utils.is_valid_uuid
import data.common.utils.jwt.decode_token as decode

default allow = false

allow if{
    input.method == "GET"
    input.path = ["api", "v1", "users"]
    payload := decode(input.token)
    payload.role == "admin"
}

allow if {
    input.method == "GET"
    input.path = ["api", "v1", "users", user_id]
    is_valid_uuid(user_id)
    payload := decode(input.token)
    payload.role in ["admin", "viewer"]
}

allow if{
    input.method == "POST"
    input.path = ["api", "v1", "users"]
    payload := decode(input.token)
    payload.role == "admin"
}

allow if{
    input.method == "PUT"
    input.path = ["api", "v1", "users", user_id]
    is_valid_uuid(user_id)
    payload := decode(input.token)
    payload.role == "admin"
}

allow if{
    input.method == "DELETE"
    input.path = ["api", "v1", "users", user_id]
    is_valid_uuid(user_id)
    payload := decode(input.token)
    payload.role == "admin"
}
