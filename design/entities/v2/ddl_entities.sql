-- USERS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- ORGANIZATIONS
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- BANK ACCOUNTS (EUR only)
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    account_name VARCHAR(255),
    iban VARCHAR(50),
    account_type VARCHAR(50),
    balance NUMERIC(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- MERCHANTS
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- CATEGORIES
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES categories(id) ON DELETE
    SET
        NULL,
        icon VARCHAR(100),
        created_at TIMESTAMP DEFAULT NOW(),
        deleted_at TIMESTAMP NULL
);

-- TRANSACTIONS (NO SOFT DELETE)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES bank_accounts(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE
    SET
        NULL,
        amount NUMERIC(15, 2) NOT NULL,
        transaction_date DATE NOT NULL,
        booking_date DATE,
        description TEXT,
        category_id UUID REFERENCES categories(id) ON DELETE
    SET
        NULL,
        is_pending BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_account_date ON transactions(account_id, transaction_date);

-- TAGS
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

CREATE TABLE transaction_tags (
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (transaction_id, tag_id)
);

-- BUDGETS
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    period_type VARCHAR(20) CHECK (
        period_type IN ('monthly', 'quarterly', 'yearly')
    ),
    amount_limit NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- RECURRING RULES
CREATE TABLE recurring_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    expected_amount NUMERIC(15, 2),
    frequency VARCHAR(20) CHECK (frequency IN ('monthly', 'yearly')),
    last_detected DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- AUDIT LOG
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE
    SET
        NULL,
        entity_type VARCHAR(50) NOT NULL,
        -- e.g. 'transaction', 'budget'
        entity_id UUID NOT NULL,
        ACTION VARCHAR(50) NOT NULL,
        -- CREATE, UPDATE, DELETE, LOGIN, etc.
        old_values JSONB,
        new_values JSONB,
        ip_address VARCHAR(50),
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

CREATE INDEX idx_audit_user ON audit_logs(user_id);