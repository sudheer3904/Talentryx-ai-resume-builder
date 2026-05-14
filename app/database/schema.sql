-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    language VARCHAR(20) DEFAULT 'English',
    target_role VARCHAR(100),
    template_style VARCHAR(50) DEFAULT 'professional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Resume Sections Table (Stores JSON data for flexibility)
CREATE TABLE IF NOT EXISTS resume_sections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    section_name VARCHAR(50) NOT NULL, -- e.g., 'Professional Summary', 'Education'
    section_content JSON,
    sort_order INT DEFAULT 0,
    is_visible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

-- Job Roles & Descriptions (For Analysis)
CREATE TABLE IF NOT EXISTS job_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    required_skills JSON
);

-- Courses (For Recommendations)
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    provider VARCHAR(100),
    link VARCHAR(255),
    skills_covered JSON,
    language VARCHAR(20) DEFAULT 'English'
);

-- Interview History
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_role VARCHAR(100),
    score DECIMAL(5, 2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Evidence Locker
CREATE TABLE IF NOT EXISTS evidence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    claim_text VARCHAR(255),
    evidence_link VARCHAR(255),
    evidence_type VARCHAR(50), -- e.g., 'Certificate', 'Project', 'GitHub'
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);
