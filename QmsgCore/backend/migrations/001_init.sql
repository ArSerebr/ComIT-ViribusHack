-- Group chat tables for QGramm Group Chat service.
-- These tables extend the shared QGramm PostgreSQL database.
-- The QGramm core tables (users, user_sessions, etc.) must already exist.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ── Groups ────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS group_chats (
    id          TEXT        PRIMARY KEY,   -- always starts with "gr_"
    name        TEXT        NOT NULL,
    avatar_url  TEXT,
    created_by_user_id UUID NOT NULL,      -- references users(id) but no FK to keep service independent
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata    JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_group_chats_updated_at ON group_chats (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_group_chats_created_by ON group_chats (created_by_user_id);

-- ── Members ───────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS group_members (
    group_id             TEXT        NOT NULL REFERENCES group_chats(id) ON DELETE CASCADE,
    user_id              UUID        NOT NULL,
    role                 TEXT        NOT NULL DEFAULT 'member',
    joined_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unread_count         INTEGER     NOT NULL DEFAULT 0,
    last_read_message_id UUID,
    PRIMARY KEY (group_id, user_id),
    CONSTRAINT group_members_role_check CHECK (role IN ('owner', 'admin', 'member'))
);

CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members (user_id);

-- ── Messages ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS group_messages (
    id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id                 TEXT        NOT NULL REFERENCES group_chats(id) ON DELETE CASCADE,
    sender_user_id           UUID,                          -- NULL for AI messages
    message_type             TEXT        NOT NULL,
    body_ciphertext          TEXT,
    body_nonce               TEXT,
    body_tag                 TEXT,
    quoted_ciphertext        TEXT,
    quoted_nonce             TEXT,
    quoted_tag               TEXT,
    reply_to_message_id      UUID        REFERENCES group_messages(id) ON DELETE SET NULL,
    forwarded_from_message_id UUID       REFERENCES group_messages(id) ON DELETE SET NULL,
    forwarded_from_group_id  TEXT        REFERENCES group_chats(id)    ON DELETE SET NULL,
    attachment_id            UUID,                          -- opaque; validated by main backend
    metadata                 JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    edited_at                TIMESTAMPTZ,
    deleted_at               TIMESTAMPTZ,
    report_count             INTEGER     NOT NULL DEFAULT 0,
    CONSTRAINT group_messages_type_check CHECK (
        message_type IN ('text','voice_note','circular_video','media','file','system','ai_request','ai_message')
    )
);

CREATE INDEX IF NOT EXISTS idx_group_messages_group_created ON group_messages (group_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_group_messages_sender        ON group_messages (sender_user_id, created_at DESC);

-- ── Reactions ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS group_message_reactions (
    message_id UUID        NOT NULL REFERENCES group_messages(id) ON DELETE CASCADE,
    emoji      TEXT        NOT NULL,
    user_id    UUID        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (message_id, emoji, user_id)
);

-- ── Auto-update updated_at ────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION gc_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_group_chats_updated_at ON group_chats;
CREATE TRIGGER trg_group_chats_updated_at
BEFORE UPDATE ON group_chats
FOR EACH ROW
EXECUTE FUNCTION gc_set_updated_at();
