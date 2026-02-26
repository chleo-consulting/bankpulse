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
