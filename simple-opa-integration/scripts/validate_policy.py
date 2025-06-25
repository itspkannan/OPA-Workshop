import jwt
import datetime
import json
import http.client

SECRET = "mysecret"

payload = {
    "sub": "1234567890",
    "name": "Jane Doe",
    "role": "admin",
    "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
}

token = jwt.encode(payload, SECRET, algorithm="HS256")
print("🔐 Generated JWT:\n", token)

opa_input = {
    "input": {
        "token": token,
        "method": "GET",
        "path": ["users"]
    }
}
opa_input_json = json.dumps(opa_input)

conn = http.client.HTTPConnection("authz-service", 8181)
headers = {
    "Content-Type": "application/json"
}
print("\n📡 Sending request to OPA...")

conn.request(
    "POST",
    "/v1/data/simple/authz",
    body=opa_input_json,
    headers=headers
)

response = conn.getresponse()
response_body = response.read().decode()

print("\n📥 OPA Response:")
print(response_body)

conn.close()
