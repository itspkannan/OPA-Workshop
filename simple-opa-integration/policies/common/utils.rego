package common.utils

uuid_regex := "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"

is_valid_uuid(uuid) if{
    regex.match(uuid_regex, uuid)
}