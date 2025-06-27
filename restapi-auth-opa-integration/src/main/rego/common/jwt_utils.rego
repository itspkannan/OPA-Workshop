package common.utils.jwt

decode_token(token) = payload if {
    result := io.jwt.decode_verify(token,{
           "secret": "secret123",
			"iss": "pki.example.com"
        })
    [valid, _, payload] := result
    valid
}
