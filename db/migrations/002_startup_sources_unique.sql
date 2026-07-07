-- Remove duplicatas antes de adicionar a constraint
DELETE FROM startup_sources a
USING startup_sources b
WHERE a.id < b.id
  AND a.startup_id = b.startup_id
  AND a.url = b.url;

-- UNIQUE constraint para suportar ON CONFLICT DO NOTHING nos batch inserts
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_startup_sources_startup_url'
          AND conrelid = 'startup_sources'::regclass
    ) THEN
        ALTER TABLE startup_sources
        ADD CONSTRAINT uq_startup_sources_startup_url
        UNIQUE (startup_id, url);
    END IF;
END $$;
