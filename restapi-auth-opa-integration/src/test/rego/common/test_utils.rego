# METADATA
# title: UUID Validation Tests
# description: Tests for checking if a string is a valid UUID using regex
# tags: [uuid, validation]

package tests.common.utils

import data.common.utils

test_valid_uuid_passes if{
    utils.is_valid_uuid("550e8400-e29b-41d4-a716-446655440000")
}

test_invalid_uuid_fails if{
    not utils.is_valid_uuid("invalid-uuid-string")
}

test_uppercase_uuid_passes if{
    utils.is_valid_uuid("550E8400-E29B-41D4-A716-446655440000")
}

test_uuid_with_invalid_variant_fails if{
    not utils.is_valid_uuid("550e8400-e29b-41d4-1716-446655440000")  # variant should start with 8,9,a,b
}

test_uuid_with_invalid_version_fails if{
    not utils.is_valid_uuid("550e8400-e29b-61d4-a716-446655440000")  # version should be 1-5
}
