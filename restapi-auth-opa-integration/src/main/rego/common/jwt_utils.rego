package common.utils.jwt

decode_token(token) = payload if {
    result := io.jwt.decode_verify(token,{
           "secret": opa.runtime().env.JWT_TOKEN_SIGN_SECRET,
		    "iss": opa.runtime().env.JWT_ISSUER
        })
    [valid, _, payload] := result
    valid
}
