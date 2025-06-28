package tests.simple.authz

import data.simple.authz

test_admin_can_get_all_users if{
    mock_input := {
        "method": "GET",
        "path": ["api", "v1", "users"],
        "token": "mock-token"
    }

    authz.allow
        with input as mock_input
        with data.common.utils.is_valid_uuid as true
        with data.common.utils.jwt.decode_token as {"role": "admin"}
}

test_viewer_can_get_user_by_id if{
    mock_input := {
        "method": "GET",
        "path": ["api", "v1", "users", "123e4567-e89b-12d3-a456-426614174000"],
        "token": "mock-token"
    }

    authz.allow
        with input as mock_input
        with data.common.utils.is_valid_uuid as true
        with data.common.utils.jwt.decode_token as {"role": "viewer"}
}

test_admin_can_post_user if{
    mock_input := {
        "method": "POST",
        "path": ["api", "v1", "users"],
        "token": "mock-token"
    }

    authz.allow
        with input as mock_input
        with data.common.utils.is_valid_uuid as true
        with data.common.utils.jwt.decode_token as {"role": "admin"}
}

test_admin_can_put_user if{
    mock_input := {
        "method": "PUT",
        "path": ["api", "v1", "users", "123e4567-e89b-12d3-a456-426614174000"],
        "token": "mock-token"
    }

    authz.allow
        with input as mock_input
        with data.common.utils.is_valid_uuid as true
        with data.common.utils.jwt.decode_token as {"role": "admin"}
}

test_admin_can_delete_user if{
    mock_input := {
        "method": "DELETE",
        "path": ["api", "v1", "users", "123e4567-e89b-12d3-a456-426614174000"],
        "token": "mock-token"
    }

    authz.allow
        with input as mock_input
        with data.common.utils.is_valid_uuid as true
        with data.common.utils.jwt.decode_token as {"role": "admin"}
}

test_invalid_role_denied if{
    mock_input := {
        "method": "GET",
        "path": ["api", "v1", "users"],
        "token": "mock-token"
    }

    not authz.allow
        with input as mock_input
        with data.common.utils.is_valid_uuid as true
        with data.common.utils.jwt.decode_token as {"role": "guest"}
}

test_invalid_uuid_denied if{
    mock_input := {
        "method": "GET",
        "path": ["api", "v1", "users", "not-a-uuid"],
        "token": "mock-token"
    }

    not authz.allow
        with input as mock_input
        with data.common.utils.is_valid_uuid as false
        with data.common.utils.jwt.decode_token as {"role": "admin"}
}
