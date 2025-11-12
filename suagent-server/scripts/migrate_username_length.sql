-- =====================================================
-- 迁移脚本：修改用户名字段长度限制
-- 从50字符减少到20字符
-- =====================================================

-- 检查是否存在超过20个字符的用户名
SELECT username, length(username) as username_length
FROM users
WHERE length(username) > 20 AND is_deleted = false;

-- 如果没有超长用户名，则可以安全地修改字段长度
-- 如果有超长用户名，需要先处理这些用户

-- 修改用户名字段长度
ALTER TABLE users
ALTER COLUMN username TYPE VARCHAR(20);

-- 添加注释说明
COMMENT ON COLUMN users.username IS '用户名（3-20个字符，只允许大小写字母、数字和下划线）';

-- 验证修改结果
\d users

SELECT '迁移完成：用户名字段长度已限制为20个字符' as message;