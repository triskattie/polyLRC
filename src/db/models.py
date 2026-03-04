from sqlalchemy import String, Integer, Column, Boolean, UUID, DateTime, ForeignKey, Numeric
from src.db.base import Base
from sqlalchemy.sql import func
from uuid import uuid4
from enum import Enum

class TransactionType(Enum):
    FAUCET = "FAUCET"
    TRADE = "TRADE"
    ADMIN_ADJUST = "ADMIN_ADJUST"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Numeric(precision=18, scale=8), nullable=False)
    type = Column(Enum(TransactionType, native_enum=False), nullable=False)
    related_market_id = Column(UUID(as_uuid=True), nullable=True) # For adding foreign key to markets later

    created_at = Column(DateTime, server_default=func.now())
