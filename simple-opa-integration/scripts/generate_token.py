import jwt
import datetime

SECRET = "mysecret"

payload = {
    "sub": "1234567890",
    "name": "Jane Doe",
    "role": "admin",
    "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
}

token = jwt.encode(payload, SECRET, algorithm="HS256")
print(token)