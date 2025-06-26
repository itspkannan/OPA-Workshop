package common.utils.jwt
# Need to be modified for Prod usage, this is a POC
# Base64url("mysecret") = "bXlzZWNyZXQ"

decode_token(token) = payload if{
    [_, payload, _] := io.jwt.decode(token)
}