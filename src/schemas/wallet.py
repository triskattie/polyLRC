from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID

class WalletResponse(BaseModel):
    wallet_id: UUID
    balance: Decimal