import pytest


async def _register_and_login(client, email: str, password: str = "secret123") -> str:
    await client.post("/auth/register", json={"email": email, "password": password})
    response = await client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_list_tasks(client):
    token = await _register_and_login(client, "eve@example.com")

    create_response = await client.post(
        "/tasks", json={"title": "Write tests"}, headers=_auth_header(token)
    )
    assert create_response.status_code == 201
    assert create_response.json()["title"] == "Write tests"
    assert create_response.json()["status"] == "todo"

    list_response = await client.get("/tasks", headers=_auth_header(token))
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


@pytest.mark.asyncio
async def test_unauthenticated_request_is_rejected(client):
    response = await client.get("/tasks")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_task(client):
    """
    This is the authorization boundary mentioned in the project guide —
    the bug class that separates junior from mid-level code.
    """
    token_a = await _register_and_login(client, "frank@example.com")
    token_b = await _register_and_login(client, "grace@example.com")

    created = await client.post(
        "/tasks", json={"title": "Frank's private task"}, headers=_auth_header(token_a)
    )
    task_id = created.json()["id"]

    response = await client.get(f"/tasks/{task_id}", headers=_auth_header(token_b))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_task_status(client):
    token = await _register_and_login(client, "heidi@example.com")

    created = await client.post("/tasks", json={"title": "Ship it"}, headers=_auth_header(token))
    task_id = created.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}", json={"status": "done"}, headers=_auth_header(token)
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"


@pytest.mark.asyncio
async def test_delete_task(client):
    token = await _register_and_login(client, "ivan@example.com")

    created = await client.post("/tasks", json={"title": "Temporary"}, headers=_auth_header(token))
    task_id = created.json()["id"]

    delete_response = await client.delete(f"/tasks/{task_id}", headers=_auth_header(token))
    assert delete_response.status_code == 204

    get_response = await client.get(f"/tasks/{task_id}", headers=_auth_header(token))
    assert get_response.status_code == 404
