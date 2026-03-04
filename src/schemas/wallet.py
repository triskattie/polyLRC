from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

class WalletResponse(BaseModel):
    user_id: UUID
    balance: Decimal