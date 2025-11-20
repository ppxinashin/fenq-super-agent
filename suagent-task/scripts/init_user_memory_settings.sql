-- =====================================================
-- 用户长期记忆设置表初始化脚本
-- PostgreSQL 版本要求: 17
-- =====================================================

-- =====================================================
-- 创建用户长期记忆设置表 (user_memory_settings)
-- =====================================================

CREATE TABLE IF NOT EXISTS user_memory_settings (
    -- 主键和基础字段
    id BIGINT PRIMARY KEY,
    
    -- 用户长期记忆设置字段
    username VARCHAR(50) UNIQUE NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- 审计字段
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'admin',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 用户长期记忆设置表注释
COMMENT ON TABLE user_memory_settings IS '用户长期记忆设置表';
COMMENT ON COLUMN user_memory_settings.id IS '主键ID（雪花ID）';
COMMENT ON COLUMN user_memory_settings.username IS '用户名';
COMMENT ON COLUMN user_memory_settings.enabled IS '长期记忆开关（true=开启, false=关闭）';
COMMENT ON COLUMN user_memory_settings.created_at IS '创建时间';
COMMENT ON COLUMN user_memory_settings.created_by IS '创建人';
COMMENT ON COLUMN user_memory_settings.updated_at IS '更新时间';
COMMENT ON COLUMN user_memory_settings.updated_by IS '更新人';
COMMENT ON COLUMN user_memory_settings.is_deleted IS '是否删除（软删除标记）';

-- 用户长期记忆设置表索引
CREATE INDEX IF NOT EXISTS idx_user_memory_settings_username ON user_memory_settings(username) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_user_memory_settings_enabled ON user_memory_settings(enabled) WHERE is_deleted = FALSE;

-- =====================================================
-- 创建触发器（自动更新updated_at）
-- =====================================================

-- 如果触发器函数不存在则创建
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为用户长期记忆设置表添加更新时间触发器
DROP TRIGGER IF EXISTS update_user_memory_settings_updated_at ON user_memory_settings;
CREATE TRIGGER update_user_memory_settings_updated_at
    BEFORE UPDATE ON user_memory_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 完成信息
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '用户长期记忆设置表创建完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '表名: user_memory_settings';
    RAISE NOTICE '字段:';
    RAISE NOTICE '  - id (主键)';
    RAISE NOTICE '  - username (用户名，唯一)';
    RAISE NOTICE '  - enabled (开关状态，默认关闭)';
    RAISE NOTICE '  - 审计字段 (created_at, created_by, updated_at, updated_by, is_deleted)';
    RAISE NOTICE '索引:';
    RAISE NOTICE '  - idx_user_memory_settings_username';
    RAISE NOTICE '  - idx_user_memory_settings_enabled';
    RAISE NOTICE '========================================';
END $$;

