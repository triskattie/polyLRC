import pytest

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