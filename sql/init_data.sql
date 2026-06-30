## 初始数据脚本，用于插入示例用户、体检报告和口味偏好数据
USE ai_nutritionist;
-- 示例用户（密码均为123456789的SHA256）​
INSERT INTO `users` (`username`, `password_hash`, `gender`, `age`, `height_cm`, `weight_kg`, `health_goals`) VALUES
('demo_user', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'male', 35, 175, 78, '["general_health", "weight_loss"]'),
('zhangsan', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'female', 28, 162, 55, '["general_health"]'),
('lisi', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'male', 50, 170, 85, '["diabetes_control", "hypertension_control"]');
-- 示例体检报告，0x32303234E5B9B4E5BAA6E4BD93E6A380：2024年体检报告。 chaozhong:轻度超重，需注意饮食控制  zhengchang：各项指标正常 sangao：三高患者，需要严格饮食管理'
INSERT INTO `health_reports` (`user_id`, `report_name`, `fasting_glucose`, `postprandial_glucose`, `total_cholesterol`, `triglycerides`, `hdl_cholesterol`, `ldl_cholesterol`, `systolic_bp`, `diastolic_bp`, `uric_acid`, `creatinine`, `bun`, `alt`, `ast`, `hemoglobin`, `notes`) VALUES
(1, '2024年体检报告', 5.8, 9.2, 5.6, 2.1, 1.0, 3.8, 135, 88, 450, 80, 5.0, 35, 32, 132, '轻度超重，需注意饮食控制'),
(2, '2024年体检报告', 4.8, 6.5, 4.5, 1.2, 1.5, 2.8, 118, 76, 320, 70, 4.0, 22, 25, 138, '各项指标正常'),
(3, '2024年体检报告', 7.2, 12.5, 6.8, 3.5, 0.8, 4.5, 155, 98, 520, 90, 6.0, 48, 45, 126, '三高患者，需要严格饮食管理');

-- 示例口味偏好
INSERT INTO `taste_preferences` (`user_id`, `preferred_flavors`, `disliked_foods`, `preferred_cuisines`, `allergies`, `cooking_time_limit`, `difficulty_preference`, `budget_level`, `meal_count`) VALUES
(1, '["清淡","偏咸","鲜香"]', '["香菜","苦瓜"]', '["粤菜","川菜","家常菜"]', '[]', 45, 'medium', 'medium', 3),
(2, '["清淡","偏甜"]', '["肥肉","内脏"]', '["粤菜","苏菜","日料"]', '["花生"]', 60, 'easy', 'medium', 3),
(3, '["清淡"]', '["辣椒","油炸食品"]', '["家常菜","粤菜"]', '["海鲜"]', 30, 'easy', 'low', 5);