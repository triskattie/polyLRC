from pydantic import BaseModel, Field
from uuid import UUID
from src.db.models import OrderSide, OrderStatus
from decimal import Decimal
from datetime import datetime

class OrderInput(BaseModel):
    market_id: UUID
    outcome_id: UUID
    side: OrderSide
    amount: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0, lt=1)

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    market_id: UUID
    outcome_id: UUID
    side: OrderSide
    status: OrderStatus
    price: Decimal
    amount: Decimal
    remaining: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}