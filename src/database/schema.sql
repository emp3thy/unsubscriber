-- Email Unsubscriber Database Schema
-- SQLite database schema for managing email whitelists, unwanted senders,
-- action history, configuration, and multi-account management
-- Uses IF NOT EXISTS to allow safe re-initialization

-- Table 1: Whitelist
-- Stores whitelisted email addresses and domains that should never be unsubscribed
CREATE TABLE IF NOT EXISTS whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    domain TEXT,
    notes TEXT,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (email IS NOT NULL OR domain IS NOT NULL)
);

-- Table 2: Unwanted Senders
-- Stores email addresses marked as unwanted, including failed unsubscribe attempts
CREATE TABLE IF NOT EXISTS unwanted_senders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    reason TEXT,
    failed_unsubscribe BOOLEAN DEFAULT 0,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Action History
-- Logs all actions performed by the application for audit and troubleshooting
CREATE TABLE IF NOT EXISTS action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_email TEXT NOT NULL,
    action_type TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT 0,
    details TEXT
);

-- Table 4: Config
-- Stores application configuration as key-value pairs
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Table 5: Accounts
-- Stores email account credentials (encrypted) for multi-account support
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    encrypted_password TEXT NOT NULL,
    provider TEXT NOT NULL,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
-- Optimize query performance for common lookup patterns

-- Index for whitelist email lookups
CREATE INDEX IF NOT EXISTS idx_whitelist_email ON whitelist(email);

-- Index for whitelist domain lookups
CREATE INDEX IF NOT EXISTS idx_whitelist_domain ON whitelist(domain);

-- Index for unwanted sender lookups
CREATE INDEX IF NOT EXISTS idx_unwanted_email ON unwanted_senders(email);

-- Index for action history sender lookups
CREATE INDEX IF NOT EXISTS idx_action_history_sender ON action_history(sender_email);

-- Index for action history timestamp queries (for date-range filtering)
CREATE INDEX IF NOT EXISTS idx_action_history_timestamp ON action_history(timestamp);

