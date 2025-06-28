import json
import http.client
import base64
import sys
import os

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)
http_handler = logging.StreamHandler(sys.stdout)
http.client.HTTPConnection.debuglevel = 1

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_token import generate_jwt, base64url_encode

SECRET = "secret123"
secret_encoded_base64 = base64url_encode(SECRET)
print("Base64 Encoded Secret:", secret_encoded_base64)
token = generate_jwt(SECRET, 'admin', 'Jane Doe')
print("🔐 Generated JWT Token:", token)
print()

API_HOST = os.getenv("API_SERVER","restapi-auth-opa-integration")
API_PORT = os.getenv("API_PORT", 8080)

try:
    print(f"✅ Sending request to your API service...{API_HOST}:{API_PORT}")
    api_conn = http.client.HTTPConnection(API_HOST, API_PORT)
    api_headers = {
        "Authorization": f"Bearer {token}"
    }
    api_conn.request("GET", "/api/v1/users", headers=api_headers)

    api_response = api_conn.getresponse()
    api_body = api_response.read().decode()

    print("📥 API Response:")
    print(f"Status: {api_response.status}")
    print(f"Body: {api_body}")
    api_conn.close()

except Exception as e:
    print(e)
    print("❗ Error processing OPA response:", str(e))
    sys.exit(1)