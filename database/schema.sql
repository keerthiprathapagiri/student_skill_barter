-- ============================================================
-- Student Skill Barter - MySQL Database Schema
-- Run this file to initialize the database
-- ============================================================

CREATE DATABASE IF NOT EXISTS skill_barter_db;
USE skill_barter_db;

-- -------------------------------------------------------
-- Users table: stores account + profile info
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(100)  NOT NULL,
    username    VARCHAR(50)   NOT NULL UNIQUE,
    password    VARCHAR(255)  NOT NULL,          -- bcrypt hash
    bio         TEXT,
    avatar_color VARCHAR(7)   DEFAULT '#4A90D9', -- hex color for avatar
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------
-- Skills table: every skill a user offers or needs
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    skill_type ENUM('offered','needed') NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -------------------------------------------------------
-- Matches table: confirmed barter connections
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS matches (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id_1   INT NOT NULL,
    user_id_2   INT NOT NULL,
    status      ENUM('pending','accepted','rejected') DEFAULT 'accepted',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id_1) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id_2) REFERENCES users(id) ON DELETE CASCADE
);

-- -------------------------------------------------------
-- Messages table: real-time chat messages
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    sender_id   INT  NOT NULL,
    receiver_id INT  NOT NULL,
    message     TEXT NOT NULL,
    is_read     BOOLEAN   DEFAULT FALSE,
    sent_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id)   REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -------------------------------------------------------
-- Learning progress table: what users are learning
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_progress (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    learner_id   INT          NOT NULL,  -- person learning
    teacher_id   INT          NOT NULL,  -- person teaching
    skill_name   VARCHAR(100) NOT NULL,
    progress_pct INT          DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
    notes        TEXT,
    updated_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -------------------------------------------------------
-- Sample data for testing
-- -------------------------------------------------------
INSERT INTO users (full_name, username, password, bio, avatar_color) VALUES
('Alice Johnson',  'alice',  '$2b$12$LQv3c1yqBwEHFl9GQSPT5.examplehash1', 'CS student passionate about web dev', '#E74C3C'),
('Bob Smith',      'bob',    '$2b$12$LQv3c1yqBwEHFl9GQSPT5.examplehash2', 'Data science enthusiast', '#2ECC71'),
('Carol Williams', 'carol',  '$2b$12$LQv3c1yqBwEHFl9GQSPT5.examplehash3', 'Designer who loves UX', '#9B59B6'),
('David Lee',      'david',  '$2b$12$LQv3c1yqBwEHFl9GQSPT5.examplehash4', 'Backend developer, loves Python', '#E67E22');

INSERT INTO skills (user_id, skill_name, skill_type) VALUES
(1, 'Python',       'offered'),
(1, 'Flask',        'offered'),
(1, 'Photoshop',    'needed'),
(2, 'Data Science', 'offered'),
(2, 'Machine Learning','offered'),
(2, 'Python',       'needed'),
(3, 'UI/UX Design', 'offered'),
(3, 'Figma',        'offered'),
(3, 'React',        'needed'),
(4, 'Django',       'offered'),
(4, 'SQL',          'offered'),
(4, 'Machine Learning','needed');
