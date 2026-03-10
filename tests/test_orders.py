import pytest
import os

async def test_create_buy_order(client, auth_headers, open_market):
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

async def test_matching_engine_maker_partial(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    sell_response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 15,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert sell_response.status_code == 200
    sell_order_id = sell_response.json()["id"]
    buy_response = await client.post(
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
    assert buy_response.status_code == 200
    buy_body = buy_response.json()
    assert buy_body["status"] == "FILLED"
    response = await client.get(
        f"/v1/orders/{sell_order_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARTIAL"
    assert float(body["remaining"]) == 15 - 10

async def test_matching_engine_incoming_partially_across_makers(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    for i in range(2):
        await client.post(
            "/v1/orders",
            json={
                "market_id": market_id,
                "outcome_id": outcome_ids[0],
                "side": "SELL",
                "amount": 4,
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
    assert body["status"] == "PARTIAL"
    assert float(body["remaining"]) == 10 - 8

async def test_matching_engine_price_time_priority(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    expensive_response = await client.post("/v1/orders", json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 4, "price": 0.4}, headers=auth_headers)
    expensive_id = expensive_response.json()["id"]
    cheapest_response = await client.post("/v1/orders", json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 4, "price": 0.3}, headers=auth_headers)
    cheapest_id = cheapest_response.json()["id"]
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "BUY",
            "amount": 4,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FILLED"
    cheap_order = await client.get(
        f"/v1/orders/{cheapest_id}",
        headers=auth_headers
    )
    assert cheap_order.status_code == 200
    assert cheap_order.json()["status"] == "FILLED"
    expensive_order = await client.get(
        f"/v1/orders/{expensive_id}",
        headers=auth_headers
    )
    assert expensive_order.json()["status"] == "OPEN"

async def test_matching_engine_no_cross_outcome(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[1],
            "side": "BUY",
            "amount": 4,
            "price": 0.4
        },
        headers=auth_headers
    )
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 4,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert response.json()["status"] == "OPEN"

async def test_create_order_unauthenticated_returns_401(client, open_market):
    market_id, outcome_ids = open_market
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 4,
            "price": 0.4
        }
    )
    assert response.status_code == 401

async def test_create_order_market_not_found_returns_404(client, auth_headers, open_market):
    market_id = "00000000-0000-0000-0000-000000000000"
    _, outcome_ids = open_market
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 4,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert response.status_code == 404

async def test_create_order_market_not_open_returns_409(client, auth_headers, admin_headers):
    VALID_MARKET = {
        "title": "Will these tests fail?",
        "description": "A simple yes or no valid_market.",
        "outcomes": [
            {"name": "Yes", "description": "The tests fail"},
            {"name": "No", "description": "The tests succeed"}
        ]
    }
    market_response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    market_id = market_response.json()["market_id"]
    outcome_ids = market_response.json()["outcome_ids"]

    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 4,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert response.status_code == 409

async def test_create_order_outcome_not_in_market_returns_404(client, auth_headers, open_market):
    market_id, _ = open_market
    outcome_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_id,
            "side": "SELL",
            "amount": 4,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert response.status_code == 404

async def test_create_order_price_out_of_range_returns_422(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 4,
            "price": 10
        },
        headers=auth_headers
    )
    assert response.status_code == 422

async def test_create_order_amount_negative_returns_422(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": -10,
            "price": 0.4
        },
        headers=auth_headers
    )
    assert response.status_code == 422

async def test_create_order_missing_balance_returns_422(client, auth_headers, open_market):
    FAUCET_AMOUNT = int(os.getenv("FAUCET_AMOUNT"))
    market_id, outcome_ids = open_market
    response = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "BUY",
            "amount": FAUCET_AMOUNT*2,
            "price": 0.8
        },
        headers=auth_headers
    )
    assert response.status_code == 422

async def test_get_order_unauthenticated_returns_401(client):
    order_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/v1/orders/{order_id}"
    )
    assert response.status_code == 401

async def test_get_order_not_found_returns_404(client, auth_headers):
    order_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/v1/orders/{order_id}",
        headers=auth_headers
    )
    assert response.status_code == 404

async def test_get_order_from_other_user_returns_403(client, auth_headers, admin_headers, open_market):
    market_id, outcome_ids = open_market
    order = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "BUY",
            "amount": 10,
            "price": 0.4
        },
        headers=admin_headers
    )
    order_id = order.json()["id"]
    response = await client.get(
        f"/v1/orders/{order_id}",
        headers=auth_headers
    )
    assert response.status_code == 403

async def test_get_order_by_id(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    order = await client.post(
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
    order_id = order.json()["id"]
    response = await client.get(
        f"/v1/orders/{order_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "id" in response.json()

async def test_seller_balance_increases(client, auth_headers, open_market, admin_headers):
    market_id, outcome_ids = open_market
    sell_order = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "BUY",
            "amount": 10,
            "price": 0.4
        },
        headers=admin_headers
    )
    assert sell_order.status_code == 200
    wallet_before = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    balance_before = float(wallet_before.json()["balance"])
    buy_order = await client.post(
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
    assert buy_order.status_code == 200
    assert buy_order.json()["status"] == "FILLED"
    wallet_after = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    balance_after = float(wallet_after.json()["balance"])
    assert balance_after == balance_before + 4

async def test_buyer_balance_decreases(client, auth_headers, open_market, admin_headers):
    market_id, outcome_ids = open_market
    sell_order = await client.post(
        "/v1/orders",
        json={
            "market_id": market_id,
            "outcome_id": outcome_ids[0],
            "side": "SELL",
            "amount": 10,
            "price": 0.4
        },
        headers=admin_headers
    )
    assert sell_order.status_code == 200
    wallet_before = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    balance_before = float(wallet_before.json()["balance"])
    buy_order = await client.post(
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
    assert buy_order.status_code == 200
    assert buy_order.json()["status"] == "FILLED"
    wallet_after = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    balance_after = float(wallet_after.json()["balance"])
    assert balance_after == balance_before - 4

async def test_no_balance_change_if_resting_order(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    before_wallet = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    before_balance = before_wallet.json()["balance"]
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
            "price": 0.5
        },
        headers=auth_headers
    )
    after_wallet = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    after_balance = after_wallet.json()["balance"]
    assert before_balance == after_balance

