-- USERS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- ORGANIZATION (optional for B2B / multi-tenant)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now()
);

-- BANK CONNECTION (Open Banking provider link)
CREATE TABLE bank_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    provider_name VARCHAR(100) NOT NULL,
    external_connection_id VARCHAR(255),
    status VARCHAR(50), -- active, expired, revoked
    created_at TIMESTAMP DEFAULT now()
);

-- BANK ACCOUNTS
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID REFERENCES bank_connections(id),
    account_name VARCHAR(255),
    iban VARCHAR(50),
    currency VARCHAR(10) NOT NULL,
    account_type VARCHAR(50), -- checking, savings, credit_card
    balance NUMERIC(15,2),
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT now()
);

-- MERCHANTS
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    normalized_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT now()
);

-- CATEGORIES
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    icon VARCHAR(100),
    created_at TIMESTAMP DEFAULT now()
);

-- TRANSACTIONS
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES bank_accounts(id),
    merchant_id UUID REFERENCES merchants(id),
    external_transaction_id VARCHAR(255),
    amount NUMERIC(15,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    transaction_date DATE NOT NULL,
    booking_date DATE,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    is_pending BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_transactions_account_date 
ON transactions(account_id, transaction_date);

-- TAGS
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE transaction_tags (
    transaction_id UUID REFERENCES transactions(id),
    tag_id UUID REFERENCES tags(id),
    PRIMARY KEY (transaction_id, tag_id)
);

-- BUDGETS
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    category_id UUID REFERENCES categories(id),
    period_type VARCHAR(20), -- monthly, quarterly, yearly
    amount_limit NUMERIC(15,2),
    created_at TIMESTAMP DEFAULT now()
);

-- RECURRING RULES (subscriptions detection)
CREATE TABLE recurring_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id),
    expected_amount NUMERIC(15,2),
    frequency VARCHAR(50), -- monthly, yearly
    last_detected DATE
);

-- EXCHANGE RATES (multi-currency)
CREATE TABLE exchange_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_currency VARCHAR(10),
    target_currency VARCHAR(10),
    rate NUMERIC(15,6),
    rate_date DATE
);