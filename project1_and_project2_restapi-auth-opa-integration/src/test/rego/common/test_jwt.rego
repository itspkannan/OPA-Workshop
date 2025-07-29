# METADATA
# title: JWT Decode Tests
# description: Tests for verifying JWT decoding and validation
# tags: [jwt, decode, token, auth]

package tests.common.utils.jwt

import data.common.utils.jwt

test_valid_token_decodes if {
  token := "eyJhbGciOiJIUzI1NiIsImtpZCI6InNhbXBsZS1hcHAiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJwa2kuZXhhbXBsZS5jb20iLCJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzU0Njc1MzAyfQ.GwQ6ZtWyLPSnSLdqaAL5rY2v5FzBZQdk8e8BZz2cVLE"
  payload := jwt.decode_token(token)
  payload.name == "Jane Doe"
  payload.sub == "1234567890"
}

test_token_with_wrong_issuer_fails if{
  token := "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwiaXNzIjoid3JvbmctaXNzdWVyLmNvbSJ9.H_YUOPb_OAXdlAHM8pvKoANvdkOMjI0w4EVyZcxdnNI"
  not jwt.decode_token(token)
}

test_token_with_wrong_secret_fails if{
  token := "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIiwiaXNzIjoicGtpLmV4YW1wbGUuY29tIn0.FAKE_INVALID_SIGNATURE_XYZ123"
  not jwt.decode_token(token)
}
