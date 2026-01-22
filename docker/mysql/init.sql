-- Flora 数据库初始化脚本
-- 创建各服务所需的数据库

CREATE DATABASE IF NOT EXISTS flora_events CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS flora_interaction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS flora_tasks CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS flora_trigger CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授权（如果使用非 root 用户）
-- GRANT ALL PRIVILEGES ON flora_events.* TO 'flora'@'%';
-- GRANT ALL PRIVILEGES ON flora_interaction.* TO 'flora'@'%';
-- GRANT ALL PRIVILEGES ON flora_tasks.* TO 'flora'@'%';
-- GRANT ALL PRIVILEGES ON flora_trigger.* TO 'flora'@'%';
-- FLUSH PRIVILEGES;
