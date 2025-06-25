import pytest

@pytest.mark.asyncio
async def test_get_users(test_app, mock_user_service):
    mock_user_service.get_all.return_value = [(1, "Alice"), (2, "Bob")]

    request, response = await test_app.asgi_client.get("/api/v1/users")
    assert response.status == 200
    assert response.json == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    mock_user_service.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_create_user(test_app, mock_user_service):
    request, response = await test_app.asgi_client.post("/api/v1/users", json={"name": "Charlie"})

    assert response.status == 201
    assert response.json == {"status": "created"}
    mock_user_service.create.assert_called_once_with("Charlie")


@pytest.mark.asyncio
async def test_update_user(test_app, mock_user_service):
    request, response = await test_app.asgi_client.put("/api/v1/users/1", json={"name": "Updated"})

    assert response.status == 200
    assert response.json == {"status": "updated"}
    mock_user_service.update.assert_called_once_with(1, "Updated")


@pytest.mark.asyncio
async def test_delete_user(test_app, mock_user_service):
    request, response = await test_app.asgi_client.delete("/api/v1/users/1")

    assert response.status == 200
    assert response.json == {"status": "deleted"}
    mock_user_service.delete.assert_called_once_with(1)
