import pytest
from datetime import datetime, timezone, timedelta


def future_timestamp(minutes: int = 60):
    return (datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)).isoformat()

VALID_MARKET = {
    "title": "Will these tests fail?",
    "description": "A simple yes or no valid_market.",
    "outcomes": [
        {"name": "Yes", "description": "The tests fail"},
        {"name": "No", "description": "The tests succeed"}
    ]
}

INVALID_MARKETS = [
    (
        "empty title",
        {**VALID_MARKET, "title": "   "}
    ),
    (
        "single outcome",
        {**VALID_MARKET, "outcomes": [{"name": "Only one", "description": ""}]}
    ),
    (
        "duplicate outcomes",
        {**VALID_MARKET, "outcomes": [
            {"name": "Yes", "description": ""},
            {"name": "yes", "description": ""}
        ]}
    ),
    (
        "closed before open",
        {**VALID_MARKET, "open_timestamp": future_timestamp(60), "closed_timestamp": future_timestamp(30)}
    ),
    (
        "open in past",
        {**VALID_MARKET, "open_timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()}
    )
]

async def test_create_market_admin(client, admin_headers):
    response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert "market_id" in body
    assert len(body["outcome_ids"]) == 2

async def test_create_market_as_user_returns_401(client, auth_headers):
    response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=auth_headers
    )
    assert response.status_code == 401

async def test_create_market_unauthenticated_returns_401(client):
    response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
    )
    assert response.status_code == 401

@pytest.mark.parametrize("case,payload", INVALID_MARKETS, ids=[c[0] for c in INVALID_MARKETS])
async def test_create_market_invalid_input_returns_400(client, admin_headers, case, payload):
    response = await client.post(
        "/v1/markets",
        json=payload,
        headers=admin_headers
    )
    assert response.status_code == 400

async def test_list_markets_empty(client, auth_headers):
    response = await client.get(
        "/v1/markets",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["markets"] == []
    assert body["total"] == 0

@pytest.mark.integration
async def test_list_markets_after_creation(client, auth_headers, admin_headers):
    await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    response = await client.get(
        "/v1/markets",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1

@pytest.mark.integration
async def test_list_market_pagination(client, auth_headers, admin_headers):
    for i in range(5):
        await client.post(
            "/v1/markets",
            json={**VALID_MARKET, "title": f"Market {i}"},
            headers=admin_headers
        )
    response = await client.get(
        "/v1/markets?limit=2",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["markets"]) == 2
    assert body["total"] == 5

@pytest.mark.integration
async def test_get_market_by_id(client, auth_headers, admin_headers):
    create_response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    market_id = create_response.json()["market_id"]

    response = await client.get(
        f"/v1/markets/{market_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == market_id
    assert body["title"] == VALID_MARKET["title"]
    assert len(body["outcomes"]) == 2

async def test_get_market_not_found_returns_404(client, auth_headers):
    response = await client.get(
        "/v1/markets/00000000-0000-0000-0000-000000000000",
        headers=auth_headers
    )
    assert response.status_code == 404

@pytest.mark.integration
async def test_patch_market_title(client, admin_headers):
    create_response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    market_id = create_response.json()["market_id"]

    response = await client.patch(
        f"/v1/markets/{market_id}",
        json={"title": "New title"},
        headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New title"

async def test_patch_as_user_returns_401(client, auth_headers, admin_headers):
    create_response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    market_id = create_response.json()["market_id"]
    
    response = await client.patch(
        f"/v1/markets/{market_id}",
        json={"title": "Hacked"},
        headers=auth_headers
    )
    assert response.status_code == 401

async def test_patch_not_found_returns_404(client, admin_headers):
    response = await client.patch(
        "/v1/markets/00000000-0000-0000-0000-000000000000",
        json={"title": "Not found"},
        headers=admin_headers
    )
    assert response.status_code == 404

async def test_patch_open_market_returns_409(client, admin_headers, db_session):
    create_response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    market_id = create_response.json()["market_id"]

    await client.patch(
        f"/v1/markets/{market_id}",
        json={"state": "OPEN"},
        headers=admin_headers
    )

    response = await client.patch(
        f"/v1/markets/{market_id}",
        json={"title": "Can't change this when market state is open"},
        headers=admin_headers
    )
    assert response.status_code == 409

async def test_orderbook_empty_new_market(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["bids"] == []
    assert response.json()["asks"] == []

async def test_orderbook_resting_buy_order(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["bids"]) == 1

async def test_orderbook_resting_sell_order(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["asks"]) == 1

async def test_orderbook_filled_get_removed(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 60, "price": 0.4},
        headers=auth_headers
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["asks"]) == 0
    assert len(body["bids"]) == 1

async def test_orderbook_bids_highest_price_first(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 60, "price": 0.5},
        headers=auth_headers
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["bids"][0]["price"] > body["bids"][1]["price"]

async def test_orderbook_asks_lowest_price_first(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 60, "price": 0.5},
        headers=auth_headers
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["asks"][0]["price"] < body["asks"][1]["price"]

async def test_orderbook_partial_orders_show_remaining(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.5},
        headers=auth_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 60, "price": 0.4},
        headers=auth_headers
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert float(body["asks"][0]["remaining"]) == 20

async def test_orderbook_unauthenticated_returns_401(client, open_market):
    market_id, outcome_ids = open_market
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}"
    )
    assert response.status_code == 401

async def test_orderbook_market_not_found_returns_404(client, auth_headers, open_market):
    _, outcome_ids = open_market
    market_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 404

async def test_orderbook_outcome_not_in_market_returns_404(client, auth_headers, open_market):
    market_id, _ = open_market
    outcome_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_id}",
        headers=auth_headers
    )
    assert response.status_code == 404