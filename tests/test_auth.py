import pytest

async def test_register_returns_tokens(client):
    response = await client.post(
        "/v1/auth/register",
        json={"email": "strongo01@example.com", "password": "B3co1s34sy!"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "refresh_token" in body
    assert "access_token" in body
    assert body["token_type"] == "bearer"

async def test_register_duplicate_email_returns_409(client):
    payload = {"email": "duplicate@xample.com", "password": "psswr!d!!"}
    await client.post("/v1/auth/register", json=payload)
    response = await client.post("/v1/auth/register", json=payload)
    assert response.status_code == 409

async def test_login_positive(client):
    credentials = {"email": "great@success.com", "password": "mypassword"}
    await client.post("/v1/auth/register", json=credentials)
    response = await client.post("/v1/auth/login", json=credentials)
    assert response.status_code == 200
    body = response.json()
    assert "refresh_token" in body
    assert "access_token" in body
    assert body["token_type"] == "bearer"

async def test_login_wrong_password_returns_401(client):
    await client.post("/v1/auth/register", json={"email": "forgetful@example.com", "password": "1mforgetting,this"})
    response = await client.post("/v1/auth/login", json={"email": "forgetful@example.com", "password": "1forgot,this"})
    assert response.status_code == 401

async def test_login_unknown_email_returns_401(client):
    await client.post("v1/auth/register", json={"email": "correct@email.com", "password": "s1mplepassword!"})
    response = await client.post("/v1/auth/login", json={"email": "incorrect@email.com", "password": "s1mplepassword!"})
    assert response.status_code == 401

async def test_refresh_returns_tokens(client, user_tokens):
    response = await client.post(
        "/v1/auth/refresh",
        json={"refresh_token": user_tokens["refresh_token"]}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["access_token"] != user_tokens["access_token"]
    assert "refresh_token" in body
    assert body["refresh_token"] != user_tokens["refresh_token"]

async def test_refresh_token_is_rotated(client, user_tokens, db_session):
    from sqlalchemy import text
    await client.post(
        "/v1/auth/refresh",
        json={"refresh_token": user_tokens["refresh_token"]}
    )
    result = await db_session.execute(
        text("SELECT 1 FROM refresh_tokens WHERE revoked = 1")
    )
    assert result.scalar() >= 1

async def test_refresh_with_random_token_returns_401(client):
    response = await client.post(
        "/v1/auth/refresh",
        json={"refresh_token": "random.garbage"}
    )
    assert response.status_code == 401

async def test_users_me_returns_user(client, auth_headers, registered_user):
    response = await client.get(
        "/v1/users/me",
        headers=auth_headers
    )
    _, email, _ = registered_user
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == email

async def test_users_me_without_headers_returns_401(client):
    response = await client.get(
        "/v1/users/me"
    )
    assert response.status_code == 401

async def test_users_me_with_revoked_token_returns_401(client, auth_headers, mock_redis):
    mock_redis.is_access_token.return_value = False
    response = await client.get(
        "/v1/users/me",
        headers=auth_headers
    )
    assert response.status_code == 401