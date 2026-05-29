-- ============================================================
-- ISH TOP AI — full schema (13 tables)
-- ============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    user_id          INTEGER PRIMARY KEY,           -- Telegram user id
    username         TEXT,
    full_name        TEXT,
    language         TEXT DEFAULT 'uz',
    coin_balance     REAL NOT NULL DEFAULT 0,
    plan             TEXT NOT NULL DEFAULT 'free',  -- free | premium | premium_plus
    plan_expires_at  TIMESTAMP,
    referrer_id      INTEGER,
    is_blocked       INTEGER NOT NULL DEFAULT 0,
    block_reason     TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users(user_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_users_username   ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_plan       ON users(plan);
CREATE INDEX IF NOT EXISTS idx_users_referrer   ON users(referrer_id);

-- 2. Referrals
CREATE TABLE IF NOT EXISTS referrals (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id      INTEGER NOT NULL,
    referred_id      INTEGER NOT NULL UNIQUE,
    coins_awarded    REAL NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users(user_id),
    FOREIGN KEY (referred_id) REFERENCES users(user_id)
);

-- 3. Subscriptions (history)
CREATE TABLE IF NOT EXISTS subscriptions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    plan             TEXT NOT NULL,
    price            INTEGER NOT NULL,
    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at       TIMESTAMP NOT NULL,
    payment_provider TEXT,
    payment_id       TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_subs_user ON subscriptions(user_id);

-- 4. Balance ledger (immutable, audit-grade)
CREATE TABLE IF NOT EXISTS balances (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    delta            REAL NOT NULL,           -- positive = credit, negative = debit
    reason           TEXT NOT NULL,           -- signup_gift|job_unlock|referral|bonus|admin_grant|admin_remove
    related_id       TEXT,
    balance_after    REAL NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_balances_user ON balances(user_id);

-- 5. Searches
CREATE TABLE IF NOT EXISTS searches (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    query            TEXT NOT NULL,
    role             TEXT,                    -- jobseeker | employer
    parsed_keywords  TEXT,
    results_count    INTEGER DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_searches_user_date ON searches(user_id, created_at);

-- 6. Jobs (cache from parsers)
CREATE TABLE IF NOT EXISTS jobs (
    id               TEXT PRIMARY KEY,        -- hash(source + url)
    source           TEXT NOT NULL,           -- hh_uz, olx, jooble, linkedin, indeed, tg
    title            TEXT NOT NULL,
    company          TEXT,
    location         TEXT,
    salary           TEXT,
    url              TEXT NOT NULL,
    description      TEXT,
    contact          TEXT,
    is_remote        INTEGER DEFAULT 0,
    keywords         TEXT,
    ai_match_score   INTEGER,
    ai_scam_risk     INTEGER,
    ai_summary       TEXT,
    fetched_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_fetched ON jobs(fetched_at);

-- 7. Saved jobs
CREATE TABLE IF NOT EXISTS saved_jobs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    job_id           TEXT NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id)  REFERENCES jobs(id)       ON DELETE CASCADE
);

-- 8. AI logs
CREATE TABLE IF NOT EXISTS ai_logs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    kind             TEXT NOT NULL,           -- analyze|advisor|scam|salary|intent_block
    prompt           TEXT,
    response         TEXT,
    tokens_in        INTEGER,
    tokens_out       INTEGER,
    cost_usd         REAL,
    blocked          INTEGER DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 9. Admin logs
CREATE TABLE IF NOT EXISTS admin_logs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id         INTEGER NOT NULL,
    action           TEXT NOT NULL,
    target_user      INTEGER,
    payload          TEXT,
    ip               TEXT,
    success          INTEGER DEFAULT 1,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin ON admin_logs(admin_id);

-- 10. Bonus channels
CREATE TABLE IF NOT EXISTS bonus_channels (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id          INTEGER NOT NULL UNIQUE,
    title            TEXT NOT NULL,
    invite_link      TEXT NOT NULL,
    reward           REAL NOT NULL DEFAULT 0.5,
    enabled          INTEGER DEFAULT 1,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bonus_claims (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    channel_id       INTEGER NOT NULL,
    coins            REAL NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, channel_id),
    FOREIGN KEY (user_id)    REFERENCES users(user_id)         ON DELETE CASCADE,
    FOREIGN KEY (channel_id) REFERENCES bonus_channels(id)     ON DELETE CASCADE
);

-- 11. Broadcasts
CREATE TABLE IF NOT EXISTS broadcasts (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id         INTEGER NOT NULL,
    text             TEXT NOT NULL,
    photo_file_id    TEXT,
    sent_count       INTEGER DEFAULT 0,
    failed_count     INTEGER DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at      TIMESTAMP
);

-- 12. Blocks history
CREATE TABLE IF NOT EXISTS blocks (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    admin_id         INTEGER NOT NULL,
    action           TEXT NOT NULL,           -- block | unblock
    reason           TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 13. Sessions (admin)
CREATE TABLE IF NOT EXISTS sessions (
    token            TEXT PRIMARY KEY,
    admin_id         INTEGER NOT NULL,
    expires_at       TIMESTAMP NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sessions_admin ON sessions(admin_id);
