// Types API BankPulse

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  first_name: string
  last_name: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
  first_name: string
  last_name: string
  created_at: string
}

export interface ApiError {
  message: string
  detail?: string | { msg: string; type: string }[]
}

// Dashboard
export interface MonthlySummary {
  current: number
  previous: number
  delta_pct: number
}

export interface DashboardSummary {
  total_balance: number
  expenses: MonthlySummary
}

export interface CategoryBreakdownItem {
  category_id: string
  category_name: string
  parent_category_name: string | null
  amount: number
  percentage: number
  transaction_count: number
}

export interface CategoriesBreakdown {
  month: string
  items: CategoryBreakdownItem[]
  total_amount: number
}

export interface TopMerchantItem {
  merchant_id: string
  merchant_name: string
  amount: number
  transaction_count: number
}

export interface TopMerchants {
  month: string
  items: TopMerchantItem[]
}

export interface RecurringSubscription {
  recurring_rule_id: string
  merchant_id: string
  merchant_name: string
  expected_amount: number | null
  frequency: string
  last_detected: string | null
  next_expected: string | null
}

export interface RecurringSubscriptions {
  items: RecurringSubscription[]
}
