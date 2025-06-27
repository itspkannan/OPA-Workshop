import aiohttp

from restapi_auth_opa_integration.config.auth_config import AuthConfig


class AuthorizationService:
    def __init__(self, config: AuthConfig):
        self.config = config

    async def is_allowed(self, token: str, method: str, path: str) -> bool:
        input_data = {
            "input": {
                "method": method,
                "path": path.strip("/").split("/"),
                "token": token
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.config.url, json=input_data) as response:
                data = await response.json()
                return data.get("result", False)