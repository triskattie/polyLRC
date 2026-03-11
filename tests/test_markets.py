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
    await client.post(f"/v1/markets/{market_id}/seed", json={"amount": 1000}, headers=admin_headers)
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
    assert len(response.json()["asks"]) == 1
    assert float(response.json()["asks"][0]["price"]) == 0.5

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
    assert len(body["asks"]) == 2

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
    assert len(body["asks"]) == 1
    assert float(body["asks"][0]["price"]) == 0.5
    assert len(body["bids"]) == 1

async def test_orderbook_bids_highest_price_first(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.3},
        headers=auth_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 60, "price": 0.2},
        headers=auth_headers
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["bids"]) == 2
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
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.6},
        headers=auth_headers,
    )
    response = await client.get(
        f"/v1/markets/{market_id}/orderbook/{outcome_ids[0]}",
        headers=auth_headers,
    )
    body = response.json()
    assert float(body["asks"][0]["price"]) == 0.5
    assert float(body["asks"][0]["remaining"]) == 960

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

async def test_resolution_unauthenticated_returns_401(client, open_market):
    market_id, outcome_ids = open_market
    response = await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[0]}
    )
    assert response.status_code == 401

async def test_resolution_non_admin_returns_401(client, auth_headers, open_market):
    market_id, outcome_ids = open_market
    response = await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[0]},
        headers=auth_headers
    )
    assert response.status_code == 401

async def test_resolution_market_not_found_returns_404(client, admin_headers, open_market):
    _, outcome_ids = open_market
    market_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[0]},
        headers=admin_headers
    )
    assert response.status_code == 404

async def test_resolution_outcome_not_in_market_returns_404(client, admin_headers, open_market):
    market_id, _ = open_market
    outcome_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_id},
        headers=admin_headers
    )
    assert response.status_code == 404

async def test_resolution_market_in_pre_returns_409(client, admin_headers):
    market_response = await client.post(
        "/v1/markets",
        json=VALID_MARKET,
        headers=admin_headers
    )
    market_id = market_response.json()["market_id"]
    outcome_id = market_response.json()["outcome_ids"][0]
    response = await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_id},
        headers=admin_headers
    )
    assert response.status_code == 409

async def test_resolution_market_already_resolved_returns_409(client, admin_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[0]},
        headers=admin_headers
    )
    response = await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[0]},
        headers=admin_headers
    )
    assert response.status_code == 409

async def test_resolution_success(client, admin_headers, open_market):
    market_id, outcome_ids = open_market
    response = await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[0]},
        headers=admin_headers
    )
    assert response.status_code == 200
    assert "id" in response.json()

async def test_resolution_correct_wallet_increase(client, auth_headers, admin_headers, open_market):
    market_id, outcome_ids = open_market
    before_wallet = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    before_balance = float(before_wallet.json()["balance"])
    
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 40, "price": 0.4},
        headers=admin_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[0]},
        headers=admin_headers
    )
    after_wallet = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    after_balance = float(after_wallet.json()["balance"])
    assert after_balance == before_balance + 24

async def test_resolution_no_winning_position_no_payout(client, auth_headers, admin_headers, open_market):
    market_id, outcome_ids = open_market
    before_wallet = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    before_balance = float(before_wallet.json()["balance"])
    
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 40, "price": 0.4},
        headers=admin_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[1]},
        headers=admin_headers
    )
    after_wallet = await client.get(
        "/v1/wallet",
        headers=auth_headers
    )
    after_balance = float(after_wallet.json()["balance"])
    assert after_balance == before_balance - 16

async def test_resolution_positions_cleared(client, auth_headers, admin_headers, open_market, db_session):
    from sqlalchemy import text
    market_id, outcome_ids = open_market
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 40, "price": 0.4},
        headers=admin_headers
    )
    await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "BUY", "amount": 40, "price": 0.4},
        headers=auth_headers
    )
    await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[1]},
        headers=admin_headers
    )
    result = await db_session.execute(text("SELECT * FROM positions WHERE outcome_id == :o"), {"o": outcome_ids[0]})
    assert result.all() == []
    
async def test_resolution_trading_lock(client, admin_headers, open_market):
    market_id, outcome_ids = open_market
    await client.post(
        f"/v1/markets/{market_id}/resolve",
        json={"winning_outcome_id": outcome_ids[1]},
        headers=admin_headers
    )
    response = await client.post(
        "/v1/orders",
        json={"market_id": market_id, "outcome_id": outcome_ids[0], "side": "SELL", "amount": 40, "price": 0.4},
        headers=admin_headers
    )
    assert response.status_code == 409

async def test_seed_unauthenticated_returns_401(client, admin_headers):
    market = await client.post("/v1/markets", json=VALID_MARKET, headers=admin_headers)
    market_id = market.json()["market_id"]

    response = await client.post(f"/v1/markets/{market_id}/seed", json={"amount": 1000})
    assert response.status_code == 401

async def test_seed_as_user_returns_401(client, admin_headers, auth_headers):
    market = await client.post("/v1/markets", json=VALID_MARKET, headers=admin_headers)
    market_id = market.json()["market_id"]

    response = await client.post(f"/v1/markets/{market_id}/seed", json={"amount": 1000}, headers=auth_headers)
    assert response.status_code == 401

async def test_seed_market_not_found_returns_404(client, admin_headers):
    market_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post(f"/v1/markets/{market_id}/seed", json={"amount": 1000}, headers=admin_headers)

async def test_seed_market_not_pre_returns_409(client, admin_headers, open_market):
    market_id, outcome_ids = open_market
    response = await client.post(f"/v1/markets/{market_id}/seed", json={"amount": 1000}, headers=admin_headers)

async def test_seed_success(client, admin_headers):
    market = await client.post("/v1/markets", json=VALID_MARKET, headers=admin_headers)
    market_id = market.json()["market_id"]

    response = await client.post(f"/v1/markets/{market_id}/seed", json={"amount": 1000}, headers=admin_headers)
    assert response.status_code == 200
    assert "market_id" in response.json()

async def test_market_transition_not_allowed_without_liquidity(client, admin_headers):
    market = await client.post("/v1/markets", json=VALID_MARKET, headers=admin_headers)
    market_id = market.json()["market_id"]

    response = await client.patch(f"/v1/markets/{market_id}", json={"state": "OPEN"}, headers=admin_headers)
    assert response.status_code == 409