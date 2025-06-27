import uuid
from unittest.mock import ANY

import pytest

@pytest.mark.asyncio
async def test_get_users(test_app, mock_user_service):
    user_id1, user_id2 = str(uuid.uuid4()), str(uuid.uuid4())

    mock_user_service.get_all.return_value = [(user_id1, "Alice"), (user_id2, "Bob")]

    request, response = await test_app.asgi_client.get("/api/v1/users")
    assert response.status == 200
    assert response.json == [{"id": user_id1, "name": "Alice"}, {"id": user_id2, "name": "Bob"}]
    mock_user_service.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_create_user(test_app, mock_user_service):
    request, response = await test_app.asgi_client.post("/api/v1/users", json={"name": "Charlie"})

    assert response.status == 201
    assert response.json == {"status": "created"}
    mock_user_service.create.assert_called_once_with(ANY, "Charlie")


@pytest.mark.asyncio
async def test_update_user(test_app, mock_user_service):
    user_id = uuid.uuid4()
    request, response = await test_app.asgi_client.put(f"/api/v1/users/{user_id}", json={"name": "Updated"})

    assert response.status == 200
    assert response.json == {"status": "updated"}
    mock_user_service.update.assert_called_once_with(user_id, "Updated")


@pytest.mark.asyncio
async def test_delete_user(test_app, mock_user_service):
    user_id = uuid.uuid4()
    request, response = await test_app.asgi_client.delete(f"/api/v1/users/{user_id}")

    assert response.status == 200
    assert response.json == {"status": "deleted"}
    mock_user_service.delete.assert_called_once_with(user_id)
