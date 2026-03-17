export type Market = {
  id: string
  title: string
  description: string | null
  state: "PRE" | "OPEN" | "CLOSED" | "RESOLVED"
  outcomes: Outcome[]
  winning_outcome_id: string | null
  open_timestamp: string | null
  closed_timestamp: string | null
  created_at: string
  updated_at: string
}

export type Outcome = {
  id: string
  name: string
  description: string | null
}

export type Order = {
  id: string
  user_id: string
  market_id: string
  outcome_id: string
  side: "BUY" | "SELL"
  status: "OPEN" | "PARTIAL" | "FILLED" | "CANCELLED"
  price: string
  amount: string
  remaining: string
  created_at: string
  updated_at: string
}

export type OrderbookLevel = {
  price: string
  remaining: string
}

export type Orderbook = {
  market_id: string
  outcome_id: string
  bids: OrderbookLevel[]
  asks: OrderbookLevel[]
}

export type WalletResponse = {
  wallet_id: string
  balance: string
}

export type User = {
  user_id: string
  email: string
  role: string
  created_at: string
}

export type MarketsPage = {
  markets: Market[]
  total: number
  limit: number
  offset: number
}

export type WalletTransaction = {
  transaction_id: string
  amount: string
  transaction_type: "FAUCET" | "TRADE" | "ADMIN_ADJUST" | "PAYOUT"
  created_at: string
}

export type TransactionsPage = {
  transactions: WalletTransaction[]
  total: number
  limit: number
  offset: number
}