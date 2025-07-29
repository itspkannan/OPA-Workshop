import pytest
from aioresponses import aioresponses
from restapi_auth_opa_integration.services.authorization_service import AuthorizationService
from restapi_auth_opa_integration.config.auth_config import AuthConfig

@pytest.mark.asyncio
async def test_is_allowed_true():
    config = AuthConfig(host='opa.local', port=8181, uri="/data/simple")
    service = AuthorizationService(config=config)

    with aioresponses() as mock:
        mock.post("http://opa.local:8181/data/simple", payload={"result": True})

        result = await service.is_allowed("admin", "GET", "/resource")
        assert result is True

@pytest.mark.asyncio
async def test_is_allowed_false():
    config = AuthConfig(host='opa.local', port=8181, uri="/data/simple")
    service = AuthorizationService(config=config)

    with aioresponses() as mock:
        mock.post("http://opa.local:8181/data/simple", payload={"result": False})

        result = await service.is_allowed("guest", "POST", "/admin")
        assert result is False
