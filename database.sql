-- 创建数据库
CREATE DATABASE job_data;

-- 选择数据库
USE job_data;

-- 创建职位数据表
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(255) NOT NULL,
    job_company VARCHAR(255) NOT NULL,
    job_area VARCHAR(255) NOT NULL,
    job_salary VARCHAR(255) NOT NULL,
    job_info_desc TEXT,
    job_detail_url VARCHAR(255) NOT NULL UNIQUE,  -- 添加唯一约束
    job_detail TEXT,
    job_degree VARCHAR(255),
    job_experience VARCHAR(255)
);
