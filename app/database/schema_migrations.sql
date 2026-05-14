-- Schema migrations for FlowCV-style Resume Platform
-- Run after schema.sql. Supports UTF-8 (use utf8mb4 for MySQL 5.5+).

-- Ensure resumes table has design and photo_path (if not already applied via update_schema.py)
-- ALTER TABLE resumes ADD COLUMN IF NOT EXISTS design JSON;
-- ALTER TABLE resumes ADD COLUMN IF NOT EXISTS photo_path VARCHAR(255);

-- Evidence: add optional document path for uploaded proof (e.g. certificate PDF)
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS document_path VARCHAR(255);
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Interviews: store Q&A and score for mock interview history
ALTER TABLE interviews ADD COLUMN IF NOT EXISTS answers_json JSON COMMENT 'Q&A pairs and keyword scores';
ALTER TABLE interviews ADD COLUMN IF NOT EXISTS questions_used JSON COMMENT 'Question IDs or text used';

-- Resume download format preference (optional; can be chosen at download time)
-- ALTER TABLE resumes ADD COLUMN IF NOT EXISTS default_download_format VARCHAR(20) DEFAULT 'pdf';
