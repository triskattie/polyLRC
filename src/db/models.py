from sqlalchemy import String, Integer, Column, Boolean, UUID, DateTime, ForeignKey, Numeric, Enum, Text, UniqueConstraint, Index
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

class OrderSide(PyEnum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(PyEnum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

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
    winning_outcome_id = Column(UUID(as_uuid=True), ForeignKey("market_outcomes.id", use_alter=True, name="fk_market_winning_outcome"), nullable=True)

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

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_market_outcome", "market_id", "outcome_id", "side", "status"),
        Index("ix_orders_user_id", "user_id"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=False)
    outcome_id = Column(UUID(as_uuid=True), ForeignKey("market_outcomes.id"), nullable=False)

    side = Column(Enum(OrderSide, native_enum=False), nullable=False)

    amount = Column(Numeric(precision=18, scale=8), nullable=False)
    price = Column(Numeric(precision=18, scale=8), nullable=False)
    remaining = Column(Numeric(precision=18, scale=8), nullable=False)

    status = Column(Enum(OrderStatus, native_enum=False), default=OrderStatus.OPEN, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)    

    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False)
    outcome_id = Column(UUID(as_uuid=True), ForeignKey("market_outcomes.id", ondelete="CASCADE"), nullable=False)

    buy_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    sell_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Numeric(precision=18, scale=8), nullable=False)
    price = Column(Numeric(precision=18, scale=8), nullable=False)    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (UniqueConstraint("user_id", "outcome_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False)
    outcome_id = Column(UUID(as_uuid=True), ForeignKey("market_outcomes.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Numeric(precision=18, scale=8), nullable=False)

Order.user = relationship("User", foreign_keys=[Order.user_id])
Order.market = relationship("Market", foreign_keys=[Order.market_id])
Order.outcome = relationship("MarketOutcome", foreign_keys=[Order.outcome_id])

Trade.buy_order = relationship("Order", foreign_keys=[Trade.buy_order_id])
Trade.sell_order = relationship("Order", foreign_keys=[Trade.sell_order_id])

Position.user = relationship("User", foreign_keys=[Position.user_id])
Position.outcome = relationship("MarketOutcome", foreign_keys=[Position.outcome_id])