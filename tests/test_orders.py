import pytest

async def test_create_buy_order(client, auth_headers, open_market):
    wallet_response = await client.get("/v1/wallet", headers=auth_headers)
    assert wallet_response.status_code == 200
    wallet_id = wallet_response.json()["wallet_id"]


    market_id, outcome_ids = open_market
    response = await client.post(
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
    assert response.status_code == 200
    body = response.json()
    assert body["remaining"] == body["amount"]
    assert body["status"] == "OPEN"

async def test_create_sell_order(client, auth_headers, open_market):
    wallet_response = await client.get("/v1/wallet", headers=auth_headers)
    assert wallet_response.status_code == 200
    wallet_id = wallet_response.json()["wallet_id"]


    market_id, outcome_ids = open_market
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 10,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["remaining"] == body["amount"]
    assert body["status"] == "OPEN"

async def test_matching_engine_both_filled(client, auth_headers, open_market):
    wallet_response = await client.get("/v1/wallet", headers=auth_headers)
    assert wallet_response.status_code == 200
    wallet_id = wallet_response.json()["wallet_id"]


    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 10,
            "price": 0.4
        },
        headers=auth_headers
    )
    response = await client.post(
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
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FILLED"
    assert float(body["remaining"]) == 0

