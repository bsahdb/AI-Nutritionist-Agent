-- ============================================​
-- AI营养师Agent 数据库初始化脚本​
-- ============================================​

CREATE DATABASE IF NOT EXISTS ai_nutritionist
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE ai_nutritionist;

-- 用户表​
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `gender` VARCHAR(10) DEFAULT NULL,
  `age` INT DEFAULT NULL,
  `height_cm` FLOAT DEFAULT NULL,
  `weight_kg` FLOAT DEFAULT NULL,
  `health_goals` JSON DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 体检报告表​
CREATE TABLE `health_reports` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `report_name` VARCHAR(100) NOT NULL,
  `fasting_glucose` FLOAT DEFAULT NULL COMMENT '空腹血糖(mmol/L)',
  `postprandial_glucose` FLOAT DEFAULT NULL COMMENT '餐后血糖(mmol/L)',
  `total_cholesterol` FLOAT DEFAULT NULL COMMENT '总胆固醇(mmol/L)',
  `triglycerides` FLOAT DEFAULT NULL COMMENT '甘油三酯(mmol/L)',
  `hdl_cholesterol` FLOAT DEFAULT NULL COMMENT '高密度脂蛋白(mmol/L)',
  `ldl_cholesterol` FLOAT DEFAULT NULL COMMENT '低密度脂蛋白(mmol/L)',
  `systolic_bp` INT DEFAULT NULL COMMENT '收缩压(mmHg)',
  `diastolic_bp` INT DEFAULT NULL COMMENT '舒张压(mmHg)',
  `uric_acid` FLOAT DEFAULT NULL COMMENT '尿酸(μmol/L)',
  `creatinine` FLOAT DEFAULT NULL COMMENT '肌酐(μmol/L)',
  `bun` FLOAT DEFAULT NULL COMMENT '尿素氮(mmol/L)',
  `alt` FLOAT DEFAULT NULL COMMENT '谷丙转氨酶(U/L)',
  `ast` FLOAT DEFAULT NULL COMMENT '谷草转氨酶(U/L)',
  `hemoglobin` FLOAT DEFAULT NULL COMMENT '血红蛋白(g/L)',
  `notes` TEXT DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_health_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 口味偏好表​
CREATE TABLE `taste_preferences` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL UNIQUE,
  `preferred_flavors` JSON DEFAULT NULL,
  `disliked_foods` JSON DEFAULT NULL,
  `preferred_cuisines` JSON DEFAULT NULL,
  `allergies` JSON DEFAULT NULL,
  `cooking_time_limit` INT DEFAULT 60,
  `difficulty_preference` VARCHAR(20) DEFAULT 'medium',
  `budget_level` VARCHAR(20) DEFAULT 'medium',
  `meal_count` INT DEFAULT 3,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_pref_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 周食谱计划表​
CREATE TABLE `meal_plans` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `health_summary` JSON DEFAULT NULL,
  `nutrition_goals` JSON DEFAULT NULL,
  `plan_data` JSON NOT NULL,
  `shopping_list` JSON DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_plan_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 营养知识库表​
CREATE TABLE `nutrition_knowledge` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `category` VARCHAR(50) NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `content` TEXT NOT NULL,
  `tags` JSON DEFAULT NULL,
  `source` VARCHAR(200) DEFAULT NULL,
  `embedding_id` VARCHAR(100) DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;