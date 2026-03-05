from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

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