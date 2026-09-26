import pytest


@pytest.mark.asyncio
async def test_register_new_user(client):
    response = await client.post(
        "/auth/register", json={"email": "alice@example.com", "password": "secret123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert "hashed_password" not in body  # never leak this


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client):
    payload = {"email": "bob@example.com", "password": "secret123"}
    await client.post("/auth/register", json=payload)

    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_with_correct_credentials(client):
    await client.post(
        "/auth/register", json={"email": "carol@example.com", "password": "secret123"}
    )

    response = await client.post(
        "/auth/login", data={"username": "carol@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_with_wrong_password_fails(client):
    await client.post(
        "/auth/register", json={"email": "dave@example.com", "password": "secret123"}
    )

    response = await client.post(
        "/auth/login", data={"username": "dave@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
