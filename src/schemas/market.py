from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from src.db.models import MarketState
from decimal import Decimal

class MarketOutcomeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

class MarketCreation(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str
    open_timestamp: datetime | None = None
    closed_timestamp: datetime | None = None
    outcomes: list[MarketOutcomeCreate]

class MarketCreationResponse(BaseModel):
    market_id: UUID
    outcome_ids: list[UUID]

class MarketId(BaseModel):
    market_id: UUID

class MarketOutcomeResponse(BaseModel):
    id: UUID
    name: str
    description: str | None

class MarketResponse(BaseModel):
    id: UUID
    title: str
    description: str
    state: MarketState
    open_timestamp: datetime | None
    closed_timestamp: datetime | None
    created_at: datetime
    updated_at: datetime
    outcomes: list[MarketOutcomeResponse]

class MarketsPageResponse(BaseModel):
    markets: list[MarketResponse]
    total: int
    limit: int
    offset: int

class MarketOutcomeUpdate(BaseModel):
    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    delete: bool = False

class MarketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: MarketState | None = None
    open_timestamp: datetime | None = None
    closed_timestamp: datetime | None = None
    outcomes: list[MarketOutcomeUpdate] | None = None

class OrderBookEntry(BaseModel):
    price: Decimal
    remaining: Decimal

class OrderBookResponse(BaseModel):
    market_id: UUID
    outcome_id: UUID
    bids: list[OrderBookEntry]
    asks: list[OrderBookEntry]