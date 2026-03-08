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