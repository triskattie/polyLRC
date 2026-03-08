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