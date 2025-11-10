-- =====================================================
-- Fenq Super Agent 数据库初始化脚本
-- PostgreSQL 版本要求: 17
-- =====================================================

-- =====================================================
-- 1. 创建数据库（如果不存在）
-- =====================================================
-- CREATE DATABASE super_agent_db
--     WITH 
--     OWNER = suagent
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'en_US.UTF-8'
--     LC_CTYPE = 'en_US.UTF-8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1;

-- \c super_agent_db;

-- =====================================================
-- 2. 创建枚举类型
-- =====================================================

-- 用户角色枚举
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'user');
    END IF;
END $$;

-- =====================================================
-- 3. 创建用户表 (users)
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    -- 主键和基础字段
    id BIGINT PRIMARY KEY,
    
    -- 用户信息字段
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(32) NOT NULL,
    salt VARCHAR(4) NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    
    -- 审计字段
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'admin',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 用户表注释
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '主键ID（雪花ID）';
COMMENT ON COLUMN users.username IS '用户名（唯一）';
COMMENT ON COLUMN users.password IS '密码（MD5加密）';
COMMENT ON COLUMN users.salt IS '盐值（从uuid4中取最后四位）';
COMMENT ON COLUMN users.role IS '用户角色（admin/user）';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.created_by IS '创建人';
COMMENT ON COLUMN users.updated_at IS '更新时间';
COMMENT ON COLUMN users.updated_by IS '更新人';
COMMENT ON COLUMN users.is_deleted IS '是否删除（软删除标记）';

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- =====================================================
-- 4. 创建智能体表 (agents)
-- =====================================================

CREATE TABLE IF NOT EXISTS agents (
    -- 主键和基础字段
    id BIGINT PRIMARY KEY,
    
    -- 智能体信息字段
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    tools JSONB DEFAULT '[]'::jsonb,
    mcp_enabled BOOLEAN DEFAULT FALSE,
    mcp_servers JSONB DEFAULT '{}'::jsonb,
    
    -- 审计字段
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'admin',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 智能体表注释
COMMENT ON TABLE agents IS '智能体表';
COMMENT ON COLUMN agents.id IS '主键ID（雪花ID）';
COMMENT ON COLUMN agents.agent_id IS '智能体英文名（唯一标识）';
COMMENT ON COLUMN agents.agent_name IS '智能体中文名';
COMMENT ON COLUMN agents.description IS '智能体介绍';
COMMENT ON COLUMN agents.system_prompt IS '系统提示词';
COMMENT ON COLUMN agents.tools IS '绑定工具清单（JSON数组）';
COMMENT ON COLUMN agents.mcp_enabled IS 'MCP开关';
COMMENT ON COLUMN agents.mcp_servers IS 'MCP服务器列表（JSON对象）';
COMMENT ON COLUMN agents.created_at IS '创建时间';
COMMENT ON COLUMN agents.created_by IS '创建人';
COMMENT ON COLUMN agents.updated_at IS '更新时间';
COMMENT ON COLUMN agents.updated_by IS '更新人';
COMMENT ON COLUMN agents.is_deleted IS '是否删除（软删除标记）';

-- 智能体表索引
CREATE INDEX IF NOT EXISTS idx_agents_agent_id ON agents(agent_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_agents_agent_name ON agents(agent_name) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);

-- =====================================================
-- 5. 创建会话日志表 (session_logs)
-- =====================================================

CREATE TABLE IF NOT EXISTS session_logs (
    -- 主键和基础字段
    id BIGINT PRIMARY KEY,
    
    -- 会话日志信息字段
    session_id BIGINT NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    
    -- 审计字段
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'admin',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 会话日志表注释
COMMENT ON TABLE session_logs IS '会话日志表';
COMMENT ON COLUMN session_logs.id IS '主键ID（雪花ID）';
COMMENT ON COLUMN session_logs.session_id IS '会话ID';
COMMENT ON COLUMN session_logs.agent_id IS '智能体英文名';
COMMENT ON COLUMN session_logs.role IS '角色（user/assistant/system）';
COMMENT ON COLUMN session_logs.content IS '消息内容';
COMMENT ON COLUMN session_logs.created_at IS '创建时间';
COMMENT ON COLUMN session_logs.created_by IS '创建人';
COMMENT ON COLUMN session_logs.updated_at IS '更新时间';
COMMENT ON COLUMN session_logs.updated_by IS '更新人';
COMMENT ON COLUMN session_logs.is_deleted IS '是否删除（软删除标记）';

-- 会话日志表索引
CREATE INDEX IF NOT EXISTS idx_session_logs_session_id ON session_logs(session_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_session_logs_agent_id ON session_logs(agent_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_session_logs_session_id_agent_id ON session_logs(session_id, agent_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_session_logs_session_id_created_at ON session_logs(session_id, created_at) WHERE is_deleted = FALSE;

-- =====================================================
-- 6. 创建用户长期记忆设置表 (user_memory_settings)
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
-- 7. 创建触发器函数（自动更新updated_at）
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_agents_updated_at ON agents;
CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_logs_updated_at ON session_logs;
CREATE TRIGGER update_session_logs_updated_at
    BEFORE UPDATE ON session_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_memory_settings_updated_at ON user_memory_settings;
CREATE TRIGGER update_user_memory_settings_updated_at
    BEFORE UPDATE ON user_memory_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 8. 插入示例数据（可选）
-- =====================================================

-- 插入管理员用户
-- 注意：这里使用示例数据，实际使用时请通过应用程序创建
-- 密码: admin123, 盐: 1234, MD5(admin1231234) = 0192023a7bbd73250516f069df18b500
INSERT INTO users (id, username, password, salt, role, created_by, updated_by)
VALUES (1000000000001, 'admin', '0192023a7bbd73250516f069df18b500', '1234', 'admin', 'system', 'system')
ON CONFLICT (id) DO NOTHING;

-- 插入普通用户
-- 密码: user123, 盐: 5678, MD5(user1235678) = 8621ffdbc5698829397d97767ac13db3
INSERT INTO users (id, username, password, salt, role, created_by, updated_by)
VALUES (1000000000002, 'demo_user', '8621ffdbc5698829397d97767ac13db3', '5678', 'user', 'system', 'system')
ON CONFLICT (id) DO NOTHING;

-- 插入示例智能体
INSERT INTO agents (
    id, 
    agent_id, 
    agent_name, 
    description, 
    system_prompt, 
    tools, 
    mcp_enabled, 
    mcp_servers,
    created_by,
    updated_by
)
VALUES (
    2000000000001,
    'demo_agent',
    '演示智能体',
    '这是一个用于演示的智能体',
    '你是一个友好的AI助手，帮助用户解决问题。',
    '["now_time", "web_search"]'::jsonb,
    true,
    '{
        "amap-maps": {
            "type": "sse",
            "url": "https://mcp.api-inference.modelscope.net/afbe1094621a49/sse"
        }
    }'::jsonb,
    'system',
    'system'
)
ON CONFLICT (id) DO NOTHING;

-- 插入示例会话日志
INSERT INTO session_logs (id, session_id, agent_id, role, content, created_by, updated_by)
VALUES 
    (3000000000001, 1000000001, 'demo_agent', 'user', '你好，请介绍一下你自己', 'system', 'system'),
    (3000000000002, 1000000001, 'demo_agent', 'assistant', '你好！我是演示智能体，很高兴为您服务。', 'system', 'system')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 9. 创建视图（可选）
-- =====================================================

-- 活跃用户视图（未删除的用户）
CREATE OR REPLACE VIEW v_active_users AS
SELECT 
    id,
    username,
    role,
    created_at,
    updated_at
FROM users
WHERE is_deleted = FALSE;

-- 活跃智能体视图
CREATE OR REPLACE VIEW v_active_agents AS
SELECT 
    id,
    agent_id,
    agent_name,
    description,
    mcp_enabled,
    created_at,
    updated_at
FROM agents
WHERE is_deleted = FALSE;

-- 会话统计视图
CREATE OR REPLACE VIEW v_session_stats AS
SELECT 
    session_id,
    agent_id,
    COUNT(*) as message_count,
    MIN(created_at) as session_start,
    MAX(created_at) as session_end
FROM session_logs
WHERE is_deleted = FALSE
GROUP BY session_id, agent_id;

-- 智能体统计视图
CREATE OR REPLACE VIEW v_agent_stats AS
SELECT 
    a.agent_id,
    a.agent_name,
    COUNT(DISTINCT sl.session_id) as session_count,
    COUNT(sl.id) as message_count,
    MAX(sl.created_at) as last_active_at
FROM agents a
LEFT JOIN session_logs sl ON a.agent_id = sl.agent_id AND sl.is_deleted = FALSE
WHERE a.is_deleted = FALSE
GROUP BY a.agent_id, a.agent_name;

-- =====================================================
-- 10. 授权（根据实际情况调整）
-- =====================================================

-- 授予用户权限（示例）
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO suagent;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO suagent;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO suagent;

-- =====================================================
-- 11. 完成信息
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '数据库初始化完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建的表:';
    RAISE NOTICE '  - users (用户表)';
    RAISE NOTICE '  - agents (智能体表)';
    RAISE NOTICE '  - session_logs (会话日志表)';
    RAISE NOTICE '  - user_memory_settings (用户长期记忆设置表)';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建的索引:';
    RAISE NOTICE '  - 用户表: 3个索引';
    RAISE NOTICE '  - 智能体表: 3个索引';
    RAISE NOTICE '  - 会话日志表: 4个索引';
    RAISE NOTICE '  - 用户长期记忆设置表: 2个索引';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建的视图:';
    RAISE NOTICE '  - v_active_users (活跃用户)';
    RAISE NOTICE '  - v_active_agents (活跃智能体)';
    RAISE NOTICE '  - v_session_stats (会话统计)';
    RAISE NOTICE '  - v_agent_stats (智能体统计)';
    RAISE NOTICE '========================================';
    RAISE NOTICE '示例数据:';
    RAISE NOTICE '  - 管理员用户: admin / admin123';
    RAISE NOTICE '  - 普通用户: demo_user / user123';
    RAISE NOTICE '  - 演示智能体: demo_agent';
    RAISE NOTICE '========================================';
END $$;

