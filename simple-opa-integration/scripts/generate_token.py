import jwt
import datetime
import base64

def base64url_encode(input_str: str) -> str:
    return base64.urlsafe_b64encode(input_str.encode("utf-8")).decode("utf-8").rstrip("=")

def generate_jwt(secret: str, role: str, name: str):
    payload = {
        "iss": "pki.example.com",
        "sub": "1234567890",
        "name": name,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }

    headers = {
        "kid": "sample-app"
    }

    token = jwt.encode(payload, secret, algorithm="HS256", headers=headers)
    return token

SECRET = "secret123"
secret_encoded_base64url = base64url_encode(SECRET)
print("Base64url Encoded Secret (for OPA):", secret_encoded_base64url)

token = generate_jwt(secret_encoded_base64url, 'admin', 'Jane Doe')
print("🔐 Generated JWT:\n", token)
