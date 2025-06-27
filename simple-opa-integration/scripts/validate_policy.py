import json
import http.client
import base64
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_token import generate_jwt, base64url_encode

SECRET = "secret123"
secret_encoded_base64 = base64url_encode(SECRET)
print("Base64 Encoded Secret:", secret_encoded_base64)
token = generate_jwt(SECRET, 'admin', 'Jane Doe')
print("🔐 Generated JWT Token:", token)
print()
opa_input = {
    "input": {
        "token": token,
        "method": "GET",
        "path": ["api", "v1", "users"]
    }
}
opa_input_json = json.dumps(opa_input)

conn = http.client.HTTPConnection("authz-service", 8181)
headers = {
    "Content-Type": "application/json"
}
print()
print("📡 Sending request to Authz Service...")

conn.request(
    "POST",
    "/v1/data/simple/authz",
    body=opa_input_json,
    headers=headers
)

response = conn.getresponse()
response_body = response.read().decode()
print()
print("📥 Authz Response:")
print(response_body)
print()
conn.close()
