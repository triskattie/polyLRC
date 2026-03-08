from sqlalchemy import String, Integer, Column, Boolean, UUID, DateTime, ForeignKey, Numeric, Enum, Text
from src.db.base import Base
from sqlalchemy.sql import func
from uuid import uuid4
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship

class TransactionType(PyEnum):
    FAUCET = "FAUCET"
    TRADE = "TRADE"
    ADMIN_ADJUST = "ADMIN_ADJUST"

class MarketState(PyEnum):
    PRE = "PRE"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    RESOLVED = "RESOLVED"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Numeric(precision=18, scale=8), nullable=False)
    type = Column(Enum(TransactionType, native_enum=False), nullable=False)
    related_market_id = Column(UUID(as_uuid=True), nullable=True) # For adding foreign key to markets later

    created_at = Column(DateTime(timezone=True), server_default=func.now())

User.wallet = relationship(
    "Wallet",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan"
)

Wallet.user = relationship(
    "User",
    back_populates="wallet"
)

Wallet.transactions = relationship(
    "WalletTransaction",
    back_populates="wallet",
    cascade="all, delete-orphan"
)

WalletTransaction.wallet = relationship(
    "Wallet",
    back_populates="transactions"
)

class Market(Base):
    __tablename__ = "markets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    state = Column(Enum(MarketState), default=MarketState.PRE, nullable=False)

    open_timestamp = Column(DateTime(timezone=True), nullable=True)
    closed_timestamp = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class MarketOutcome(Base):
    __tablename__ = "market_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

Market.outcomes = relationship(
    "MarketOutcome",
    back_populates="market",
    cascade="all, delete-orphan"
)

MarketOutcome.market = relationship(
    "Market",
    back_populates="outcomes"
)