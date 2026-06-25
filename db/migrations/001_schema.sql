-- ============================================================
-- Migration 001: Schema inicial do AIRadar
-- Fontes: InovAtiva, ACE Ventures, Liga Ventures, Distrito,
--         Startups.com.br
-- ============================================================

-- 1. raw_pages — cache de páginas brutas coletadas
CREATE TABLE IF NOT EXISTS raw_pages (
    id           SERIAL PRIMARY KEY,
    url          TEXT NOT NULL UNIQUE,
    fetch_method TEXT NOT NULL,         -- "playwright" | "requests"
    raw_html     TEXT,
    fetched_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 2. startups — perfil estruturado de cada startup
CREATE TABLE IF NOT EXISTS startups (
    id                      SERIAL PRIMARY KEY,
    name                    TEXT NOT NULL,
    website                 TEXT,
    sector                  TEXT,
    description             TEXT,
    founders                TEXT[],
    funding_stage           TEXT,
    funding_amount_usd      NUMERIC,
    employee_count_estimate TEXT,
    ai_signals              TEXT[],
    tech_stack_mentions     TEXT[],
    state                   TEXT,             -- UF (ex: "SP")
    business_area           TEXT,             -- área de negócio InovAtiva
    program                 TEXT,             -- nome do programa
    cohort_year             INTEGER,          -- ano da turma
    cohort_cycle            TEXT,             -- ciclo (ex: "2024-01")
    inovativa_status        TEXT,             -- status no programa
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- 3. startup_sources — rastreabilidade N:N
CREATE TABLE IF NOT EXISTS startup_sources (
    id                SERIAL PRIMARY KEY,
    startup_id        INT NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    url               TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    raw_excerpt       TEXT,
    fetched_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 4. startup_classifications — resultado do Classifier Agent
CREATE TABLE IF NOT EXISTS startup_classifications (
    id              SERIAL PRIMARY KEY,
    startup_id      INT NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    label           TEXT NOT NULL,   -- "ai_native" | "ai_enabled" | "non_ai"
    confidence      NUMERIC,         -- 0.0 a 1.0
    justification   TEXT,
    classified_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 5. nvidia_recommendations — resultado do Recommendation Agent
CREATE TABLE IF NOT EXISTS nvidia_recommendations (
    id                       SERIAL PRIMARY KEY,
    startup_id               INT NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    nvidia_technology        TEXT NOT NULL,
    technical_justification  TEXT,
    business_justification   TEXT,
    priority                 TEXT,   -- "high" | "medium" | "low"
    implementation_complexity TEXT,  -- "low" | "medium" | "high"
    suggested_next_action    TEXT,
    evidence                 TEXT[],
    created_at               TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Índices
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_startups_name              ON startups (name);
CREATE INDEX IF NOT EXISTS idx_startup_sources_startup_id ON startup_sources (startup_id);
CREATE INDEX IF NOT EXISTS idx_classifications_startup_id ON startup_classifications (startup_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_startup_id  ON nvidia_recommendations (startup_id);
