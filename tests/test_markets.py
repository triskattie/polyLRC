import pytest
from datetime import datetime, timezone, timedelta


def future_timestamp(minutes: int = 60):
    return (datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)).isoformat()

MARKET = {
    "title": "Will these tests fail?",
    "description": "A simple yes or no market.",
    "outcomes": [
        {"name": "Yes", "description": "The tests fail"},
        {"name": "No", "description": "The tests succeed"}
    ]
}

async def test_create_market_admin(client, admin_headers):
    response = await client.post(
        "/v1/markets",
        json=MARKET,
        headers=admin_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert "market_id" in body
    assert len(body["outcome_ids"]) == 2

async def test_create_market_as_user_returns_401(client, auth_headers):
    response = await client.post(
        "/v1/markets",
        json=MARKET,
        headers=auth_headers
    )
    assert response.status_code == 401

async def test_create_market_unauthenticated_returns_401(client):
    response = await client.post(
        "/v1/markets",
        json=MARKET,
    )
    assert response.status_code == 401

async def test_create_market_no_title_returns_400(client, admin_headers):
    response = await client.post(
        "/v1/markets",
        json={**MARKET, "title": "        "},
        headers=admin_headers
    )
    assert response.status_code == 400

async def test_create_market_one_outcome_returns_400(client, admin_headers):
    response = await client.post(
        "/v1/markets",
        json={**MARKET, "outcomes": [{"name": "Yes", "description": "The tests will fail"}]},
        headers=admin_headers
    )
    assert response.status_code == 400

async def test_create_market_duplicate_outcome_returns_400(client, admin_headers):
    response = await client.post(
        "/v1/markets",
        json={**MARKET, "outcomes": [{"name": "Yes", "description": "The tests will fail"}, {"name": "Yes", "description": "The tests will fail"}]},
        headers=admin_headers
    )
    assert response.status_code == 400

async def test_create_market_closed_before_open_returns_400(client, admin_headers):
    response = await client.post(
        "/v1/markets",
        json={**MARKET, "open_timestamp": future_timestamp(60), "closed_timestamp": future_timestamp(30)},
        headers=admin_headers
    )
    assert response.status_code == 400

async def test_create_market_open_in_past_returns_400(client, admin_headers):
    past = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
    response = await client.post(
        "/v1/markets",
        json={**MARKET, "open_timestamp": past},
        headers=admin_headers
    )
    assert response.status_code == 400