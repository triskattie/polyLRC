from pydantic import BaseModel
from decimal import Decimal

class WalletResponse(BaseModel):
    user_id: str
    balance: Decimal