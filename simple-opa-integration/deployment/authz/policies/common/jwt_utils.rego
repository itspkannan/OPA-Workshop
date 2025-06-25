package common.utils.jwt

# Need to be modified for Prod usage, this is a POC
# Base64url("mysecret") = "bXlzZWNyZXQ"

decode_token(token) = [valid, payload ] if {
  [valid, header, payload] := io.jwt.decode_verify(token, {
    "keys": [
        {
          "kty": "oct",
          "alg": "HS256",
          "kid": "sample-app",
          "k": "bXlzZWNyZXQ",
          "alg": "HS256"
        }
      ]
    })
}