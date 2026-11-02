-- ============================================================================
-- MoodMentor - Complete MySQL Database Schema
-- Architecture: Relational Schema with Full Constraints, Foreign Keys & Indexes
-- Engine: InnoDB
-- Collation: utf8mb4_unicode_ci
-- Tables:
--   1. users (Users)
--   2. journal_entries (JournalEntries)
--   3. emotion_results (EmotionResults)
--   4. suggestions (Suggestions)
--   5. token_blocklist (TokenBlocklist for JWT Revocation)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS moodmentor_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE moodmentor_db;

-- ----------------------------------------------------------------------------
-- 1. USERS TABLE
-- Represents registered platform members and account credentials.
-- Primary Key: id
-- Unique Constraints: email, username
-- Check Constraints: email length, fullname length
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT,
    fullname VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL,
    password VARCHAR(255) NOT NULL,
    username VARCHAR(64) NULL,
    bio TEXT NULL,
    wellness_goal VARCHAR(255) DEFAULT 'Mindfulness & Stress Reduction',
    preferred_support_style VARCHAR(100) DEFAULT 'Gentle & Compassionate',
    theme VARCHAR(50) DEFAULT 'Light Mode',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Primary Key Constraint
    CONSTRAINT pk_users PRIMARY KEY (id),

    -- Unique Constraints
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT uq_users_username UNIQUE (username),

    -- Validation Constraints
    CONSTRAINT chk_users_fullname_min CHECK (CHAR_LENGTH(TRIM(fullname)) >= 2),
    CONSTRAINT chk_users_email_valid CHECK (CHAR_LENGTH(TRIM(email)) >= 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Performance Indexes on Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at DESC);


-- ----------------------------------------------------------------------------
-- 2. JOURNAL ENTRIES TABLE (JournalEntries)
-- Stores user reflective thoughts, dates, titles, and text contents.
-- Primary Key: id
-- Foreign Key: user_id -> users(id) ON DELETE CASCADE ON UPDATE CASCADE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS journal_entries (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content MEDIUMTEXT NOT NULL,
    tags VARCHAR(255) DEFAULT '',
    entry_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Primary Key Constraint
    CONSTRAINT pk_journal_entries PRIMARY KEY (id),

    -- Foreign Key Constraint (Cascade delete ensures data integrity)
    CONSTRAINT fk_journal_entries_user FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,

    -- Validation Constraints
    CONSTRAINT chk_journal_title_not_empty CHECK (CHAR_LENGTH(TRIM(title)) > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Performance & Query Optimization Indexes on JournalEntries
CREATE INDEX idx_journal_user_id ON journal_entries(user_id);
CREATE INDEX idx_journal_entry_date ON journal_entries(entry_date);
CREATE INDEX idx_journal_user_date ON journal_entries(user_id, entry_date DESC);
CREATE INDEX idx_journal_created_at ON journal_entries(created_at DESC);
CREATE FULLTEXT INDEX ft_journal_content ON journal_entries(title, content);


-- ----------------------------------------------------------------------------
-- 3. EMOTION RESULTS TABLE (EmotionResults / emotion_results)
-- Stores deep multimodal AI analysis outputs (DistilBERT emotion classification,
-- VADER sentiment score, keyword extractions, and psychological guidance).
-- Primary Key: id
-- Unique Constraint: journal_id (Strict 1-to-1 relationship with JournalEntries)
-- Foreign Keys:
--   - journal_id -> journal_entries(id) ON DELETE CASCADE ON UPDATE CASCADE
--   - user_id -> users(id) ON DELETE CASCADE ON UPDATE CASCADE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS emotion_results (
    id INT AUTO_INCREMENT,
    journal_id INT NOT NULL,
    user_id INT NOT NULL,
    primary_emotion VARCHAR(50) NOT NULL,
    emotion_confidence DECIMAL(6,4) NOT NULL,
    confidence_percentage DECIMAL(5,2) GENERATED ALWAYS AS (ROUND(emotion_confidence * 100, 2)) STORED,
    sentiment_label VARCHAR(20) NOT NULL,
    sentiment_score DECIMAL(6,4) NOT NULL,
    sentiment_positive DECIMAL(6,4) DEFAULT 0.0000,
    sentiment_neutral DECIMAL(6,4) DEFAULT 0.0000,
    sentiment_negative DECIMAL(6,4) DEFAULT 0.0000,
    all_emotions JSON NULL,
    keywords JSON NULL,
    recommendations TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Primary Key Constraint
    CONSTRAINT pk_emotion_results PRIMARY KEY (id),

    -- Unique 1-to-1 Association with Journal Entry
    CONSTRAINT uq_emotion_results_journal UNIQUE (journal_id),

    -- Foreign Key Constraints
    CONSTRAINT fk_emotion_results_journal FOREIGN KEY (journal_id) 
        REFERENCES journal_entries(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_emotion_results_user FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,

    -- Range and Domain Validation Constraints
    CONSTRAINT chk_emotion_confidence_range CHECK (emotion_confidence >= 0.0000 AND emotion_confidence <= 1.0000),
    CONSTRAINT chk_sentiment_score_range CHECK (sentiment_score >= -1.0000 AND sentiment_score <= 1.0000),
    CONSTRAINT chk_sentiment_label_domain CHECK (sentiment_label IN ('Positive', 'Neutral', 'Negative')),
    CONSTRAINT chk_primary_emotion_domain CHECK (primary_emotion IN ('Joy', 'Fear', 'Sadness', 'Anger', 'Love', 'Surprise', 'Neutral'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Performance Indexes on EmotionResults
CREATE INDEX idx_emotion_journal_id ON emotion_results(journal_id);
CREATE INDEX idx_emotion_user_id ON emotion_results(user_id);
CREATE INDEX idx_emotion_primary ON emotion_results(primary_emotion);
CREATE INDEX idx_emotion_sentiment_label ON emotion_results(sentiment_label);
CREATE INDEX idx_emotion_user_primary ON emotion_results(user_id, primary_emotion);
CREATE INDEX idx_emotion_created_at ON emotion_results(created_at DESC);


-- ----------------------------------------------------------------------------
-- 4. SUGGESTIONS TABLE (Suggestions)
-- Stores personalized wellness activities, coping strategies, and actionable
-- micro-interventions generated for each detected emotional state.
-- Primary Key: id
-- Foreign Keys:
--   - emotion_result_id -> emotion_results(id) ON DELETE CASCADE ON UPDATE CASCADE
--   - user_id -> users(id) ON DELETE CASCADE ON UPDATE CASCADE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS suggestions (
    id INT AUTO_INCREMENT,
    emotion_result_id INT NOT NULL,
    user_id INT NOT NULL,
    emotion VARCHAR(50) NOT NULL,
    suggestion_text VARCHAR(255) NOT NULL,
    category VARCHAR(60) DEFAULT 'Wellness',
    icon VARCHAR(20) DEFAULT '✨',
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Primary Key Constraint
    CONSTRAINT pk_suggestions PRIMARY KEY (id),

    -- Foreign Key Constraints
    CONSTRAINT fk_suggestions_emotion_result FOREIGN KEY (emotion_result_id) 
        REFERENCES emotion_results(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_suggestions_user FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,

    -- Validation Constraints
    CONSTRAINT chk_suggestion_text_not_empty CHECK (CHAR_LENGTH(TRIM(suggestion_text)) > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Performance Indexes on Suggestions
CREATE INDEX idx_suggestions_emotion_result ON suggestions(emotion_result_id);
CREATE INDEX idx_suggestions_user ON suggestions(user_id);
CREATE INDEX idx_suggestions_emotion ON suggestions(emotion);
CREATE INDEX idx_suggestions_status ON suggestions(user_id, is_completed);
CREATE INDEX idx_suggestions_created_at ON suggestions(created_at DESC);


-- ----------------------------------------------------------------------------
-- 5. TOKEN BLOCKLIST TABLE (JWT Authentication & Server-Side Logout)
-- Stores revoked JWT identifiers (jti) for bulletproof token revocation.
-- Primary Key: id
-- Unique Constraint: jti
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS token_blocklist (
    id INT AUTO_INCREMENT,
    jti VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_token_blocklist PRIMARY KEY (id),
    CONSTRAINT uq_token_blocklist_jti UNIQUE (jti)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_token_blocklist_jti ON token_blocklist(jti);


-- ----------------------------------------------------------------------------
-- 6. COMPATIBILITY VIEWS (PascalCase Aliases)
-- Enables seamless cross-platform querying with both PascalCase (Users,
-- JournalEntries, EmotionResults, Suggestions) and snake_case conventions.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW Users AS SELECT * FROM users;
CREATE OR REPLACE VIEW JournalEntries AS SELECT * FROM journal_entries;
CREATE OR REPLACE VIEW EmotionResults AS SELECT * FROM emotion_results;
CREATE OR REPLACE VIEW Suggestions AS SELECT * FROM suggestions;
