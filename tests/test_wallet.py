import pytest
from sqlalchemy import text
import os

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

    faucet_amount = int(os.getenv("FAUCET_AMOUNT"))
    assert balance_after_two == faucet_amount * 3

async def test_transactions_are_empty_new_user(client, auth_headers):
    response = await client.get("/v1/wallet/transactions", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body["transactions"]) == 1
    assert float(body["total"]) == 1
    assert body["transactions"][0]["transaction_type"] == "FAUCET"

async def test_transactions_are_not_empty(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "BUY",
            "amount": 10,
            "price": 0.4
        },
        headers=auth_headers
    )
    await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 10,
            "price": 0.3
        },
        headers=auth_headers
    )
    response = await client.get("/v1/wallet/transactions", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body["transactions"]) == 3
    assert float(body["total"]) == 3

async def test_transactions_unauthorized_returns_401(client):
    response = await client.get("/v1/wallet/transactions")
    assert response.status_code == 401