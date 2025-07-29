from sanic import json, Request, HTTPResponse
class HealthCheckController:

    async def get(self, request: Request) -> HTTPResponse:
        return json({"status": "ok"})