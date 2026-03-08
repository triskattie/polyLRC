import pytest
from sqlalchemy import text


async def test_get_wallet_returns_balance(client, auth_headers):
    response = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert "balance" in body
    assert "wallet_id" in body

async def test_get_wallet_unauthenticated_returns_401(client):
    response = await client.get(
        "/v1/wallet",
    )
    assert response.status_code == 401

async def test_faucet_increases_balance(client, auth_headers):
    before_response = await client.get("/v1/wallet", headers=auth_headers)
    before_body = before_response.json()
    before_balance = before_body["balance"]
    response = await client.post("/v1/wallet/faucet", headers=auth_headers)
    assert response.status_code == 200
    after_body = response.json()
    after_balance = after_body["balance"]
    assert after_balance > before_balance

async def test_faucet_cooldown_returns_429(client, auth_headers, mock_redis):
    mock_redis.claim_faucet.return_value = False
    response = await client.post(
        "/v1/wallet/faucet",
        headers=auth_headers
    )
    assert response.status_code == 429

async def test_faucet_unauthenticated_returns_401(client):
    response = await client.post(
        "/v1/wallet/faucet"
    )
    assert response.status_code == 401

@pytest.mark.integration
async def test_balance_is_sum_of_transactions(client, auth_headers, db_session):
    first = await client.post("/v1/wallet/faucet", headers=auth_headers)
    balance_after_one = float(first.json()["balance"])

    second = await client.post("/v1/wallet/faucet", headers=auth_headers)
    balance_after_two = float(second.json()["balance"])

    assert balance_after_two + 10 == pytest.approx(balance_after_one * 2, rel=1e-6)