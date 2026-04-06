-- =============================================================
-- TalentAI MySQL Setup Script
-- Run this once to create the DB and seed sample data
-- Usage: mysql -u root -p < setup_mysql.sql
-- =============================================================

CREATE DATABASE IF NOT EXISTS talentai_db;
USE talentai_db;

-- ---------------------------------------------------------------
-- Tables
-- ---------------------------------------------------------------

CREATE TABLE IF NOT EXISTS candidates (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255)  NOT NULL,
    email       VARCHAR(255)  UNIQUE,
    phone       VARCHAR(50),
    role        VARCHAR(255),
    skills      TEXT,
    experience  FLOAT         DEFAULT 0,
    score       FLOAT         DEFAULT 0,
    status      VARCHAR(50)   DEFAULT 'Pending',
    resume_text LONGTEXT,
    uploaded_at DATETIME      DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP
                              ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_roles (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    title            VARCHAR(255) NOT NULL,
    description      TEXT,
    required_skills  TEXT,
    min_experience   FLOAT DEFAULT 0,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interviews (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id    INT,
    candidate_name  VARCHAR(255),
    role            VARCHAR(255),
    interview_date  DATE,
    interview_time  TIME,
    interviewer     VARCHAR(255),
    mode            VARCHAR(50)  DEFAULT 'Online',
    status          VARCHAR(50)  DEFAULT 'Scheduled',
    notes           TEXT,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        ON DELETE SET NULL
);

-- ---------------------------------------------------------------
-- Seed: Job Roles
-- ---------------------------------------------------------------

INSERT INTO job_roles (title, description, required_skills, min_experience) VALUES
('Data Scientist',
 'Develop machine learning models, perform statistical analysis, and derive insights from large datasets to drive business decisions.',
 'Python, SQL, Machine Learning, TensorFlow, Pandas, Statistics, Data Visualization',
 2),

('Data Analyst',
 'Analyze data, create dashboards, and generate actionable reports for business stakeholders.',
 'SQL, Excel, Power BI, Tableau, Python, Statistics',
 1),

('ML Engineer',
 'Build, deploy, and maintain machine learning pipelines and model serving infrastructure.',
 'Python, MLOps, Docker, Kubernetes, TensorFlow, PyTorch, REST APIs',
 3),

('Backend Developer',
 'Design and build scalable REST APIs and microservices using modern backend frameworks.',
 'Python, Java, Node.js, SQL, REST APIs, Docker, Redis, AWS',
 2),

('Frontend Developer',
 'Create responsive, accessible web interfaces using modern JavaScript frameworks.',
 'React, JavaScript, TypeScript, HTML, CSS, REST APIs, Git',
 1);

-- ---------------------------------------------------------------
-- Seed: Sample Candidates
-- ---------------------------------------------------------------

INSERT INTO candidates (name, email, phone, role, skills, experience, score, status, resume_text) VALUES
('Arjun Sharma',  'arjun.sharma@email.com',  '+91-9876543210', 'Data Scientist',
 'python, sql, machine learning, tensorflow, pandas, numpy, statistics',
 3.5, 0.88, 'Shortlisted',
 'Arjun Sharma - Data Scientist with 3.5 years experience. Proficient in Python, SQL, Machine Learning, TensorFlow.'),

('Priya Nair',    'priya.nair@email.com',    '+91-9876543211', 'Data Analyst',
 'sql, excel, power bi, tableau, python, statistics',
 2.0, 0.75, 'Shortlisted',
 'Priya Nair - Data Analyst. 2 years experience in SQL, Excel, Power BI and Tableau dashboards.'),

('Rohit Verma',   'rohit.verma@email.com',   '+91-9876543212', 'ML Engineer',
 'python, docker, kubernetes, tensorflow, pytorch, rest api, mlops',
 4.0, 0.91, 'Hired',
 'Rohit Verma - ML Engineer. 4 years experience in MLOps, Docker, Kubernetes, PyTorch.'),

('Sneha Patel',   'sneha.patel@email.com',   '+91-9876543213', 'Backend Developer',
 'python, java, sql, rest api, docker, aws',
 2.5, 0.70, 'Pending',
 'Sneha Patel - Backend Developer. 2.5 years in Python, Java, REST APIs, Docker, AWS.'),

('Vikram Singh',  'vikram.singh@email.com',  '+91-9876543214', 'Data Scientist',
 'python, r, sql, machine learning, pandas, statistics',
 1.5, 0.62, 'Rejected',
 'Vikram Singh - Junior Data Scientist. 1.5 years experience in R, Python, statistics.'),

('Anika Reddy',   'anika.reddy@email.com',   '+91-9876543215', 'Frontend Developer',
 'react, javascript, typescript, html, css, rest api, git',
 3.0, 0.83, 'Shortlisted',
 'Anika Reddy - Frontend Developer. 3 years experience in React, TypeScript, CSS.'),

('Karan Mehta',   'karan.mehta@email.com',   '+91-9876543216', 'ML Engineer',
 'python, tensorflow, keras, docker, rest api, git',
 2.0, 0.77, 'Pending',
 'Karan Mehta - ML Engineer. 2 years. Proficient in TensorFlow, Keras, Docker.'),

('Divya Iyer',    'divya.iyer@email.com',    '+91-9876543217', 'Data Analyst',
 'sql, excel, tableau, python, statistics, power bi',
 4.5, 0.85, 'Shortlisted',
 'Divya Iyer - Senior Data Analyst. 4.5 years. Expert in Tableau, SQL, Power BI.'),

('Raj Kumar',     'raj.kumar@email.com',     '+91-9876543218', 'Backend Developer',
 'node.js, javascript, sql, docker, aws, rest api',
 1.0, 0.55, 'Rejected',
 'Raj Kumar - Junior Backend Dev. 1 year experience in Node.js and REST APIs.'),

('Meera Joshi',   'meera.joshi@email.com',   '+91-9876543219', 'Data Scientist',
 'python, sql, deep learning, pytorch, nlp, transformers, pandas',
 5.0, 0.93, 'Hired',
 'Meera Joshi - Senior Data Scientist. 5 years. Expert in NLP, Transformers, PyTorch.');

-- ---------------------------------------------------------------
-- Seed: Sample Interviews
-- ---------------------------------------------------------------

INSERT INTO interviews (candidate_id, candidate_name, role, interview_date, interview_time, interviewer, mode, status, notes) VALUES
(1, 'Arjun Sharma', 'Data Scientist',   DATE_ADD(CURDATE(), INTERVAL 2 DAY),  '10:00:00', 'Dr. Priya Sharma',    'Online (Video Call)', 'Scheduled', 'Focus on ML model design and Python coding round'),
(2, 'Priya Nair',   'Data Analyst',     DATE_ADD(CURDATE(), INTERVAL 3 DAY),  '11:30:00', 'Rahul Gupta',         'Online (Video Call)', 'Scheduled', 'SQL test + Tableau case study'),
(6, 'Anika Reddy',  'Frontend Developer', DATE_ADD(CURDATE(), INTERVAL 5 DAY), '14:00:00', 'Tech Panel',          'In-Person',           'Scheduled', 'React component challenge'),
(8, 'Divya Iyer',   'Data Analyst',     DATE_ADD(CURDATE(), INTERVAL 7 DAY),  '09:00:00', 'Analytics Head',      'Online (Video Call)', 'Scheduled', 'Final HR round');

-- Done!
SELECT 'TalentAI database setup complete!' AS Status;
SELECT COUNT(*) AS Candidates FROM candidates;
SELECT COUNT(*) AS JobRoles   FROM job_roles;
SELECT COUNT(*) AS Interviews FROM interviews;
