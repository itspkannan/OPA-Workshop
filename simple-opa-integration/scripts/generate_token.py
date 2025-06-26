import jwt
import datetime

SECRET = "mysecret"

payload = {
    "sub": "1234567890",
    "name": "Jane Doe",
    "role": "admin",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
}

headers = {
    "kid": "sample-app"
}

token = jwt.encode(payload, SECRET, algorithm="HS256", headers=headers)
print("🔐 Generated JWT:\n", token)
