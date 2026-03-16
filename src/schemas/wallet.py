from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID
from src.db.models import TransactionType
from datetime import datetime

class WalletResponse(BaseModel):
    wallet_id: UUID
    balance: Decimal

class TransactionResponse(BaseModel):
    transaction_id: UUID
    amount: Decimal
    transaction_type: TransactionType
    created_at: datetime

class WalletTransactionsResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    limit: int
    offset: int