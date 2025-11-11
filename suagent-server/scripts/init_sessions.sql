-- =====================================================
-- 会话表(sessions) 初始化脚本
-- PostgreSQL 版本要求: 17
-- =====================================================

-- =====================================================
-- 1. 创建会话表 (sessions)
-- =====================================================

CREATE TABLE IF NOT EXISTS sessions (
    -- 主键和基础字段
    id BIGINT PRIMARY KEY,
    
    -- 会话信息字段
    agent_id VARCHAR(100) NOT NULL,
    session_id BIGINT UNIQUE NOT NULL,
    title VARCHAR(200),
    
    -- 审计字段
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'admin',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 会话表注释
COMMENT ON TABLE sessions IS '会话表';
COMMENT ON COLUMN sessions.id IS '主键ID（雪花ID）';
COMMENT ON COLUMN sessions.agent_id IS '智能体英文名';
COMMENT ON COLUMN sessions.session_id IS '会话ID（唯一）';
COMMENT ON COLUMN sessions.title IS '会话标题（第一轮对话后设置）';
COMMENT ON COLUMN sessions.created_at IS '创建时间';
COMMENT ON COLUMN sessions.created_by IS '创建人';
COMMENT ON COLUMN sessions.updated_at IS '更新时间';
COMMENT ON COLUMN sessions.updated_by IS '更新人';
COMMENT ON COLUMN sessions.is_deleted IS '是否删除（软删除标记）';

-- 会话表索引
CREATE INDEX IF NOT EXISTS idx_session_agent_id ON sessions(agent_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_session_session_id ON sessions(session_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_session_agent_id_session_id ON sessions(agent_id, session_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);

-- =====================================================
-- 2. 创建触发器（自动更新updated_at）
-- =====================================================

-- 如果触发器函数不存在，则创建
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为sessions表添加更新时间触发器
DROP TRIGGER IF EXISTS update_sessions_updated_at ON sessions;
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 3. 插入示例数据（可选）
-- =====================================================

-- 插入示例会话
INSERT INTO sessions (id, agent_id, session_id, title, created_by, updated_by)
VALUES 
    (4000000000001, 'demo_agent', 1000000001, '演示会话', 'system', 'system'),
    (4000000000002, 'demo_agent', 1000000002, '测试会话', 'system', 'system')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 4. 创建视图（可选）
-- =====================================================

-- 活跃会话视图
CREATE OR REPLACE VIEW v_active_sessions AS
SELECT 
    id,
    agent_id,
    session_id,
    title,
    created_at,
    updated_at
FROM sessions
WHERE is_deleted = FALSE;

-- 会话详情视图（关联智能体信息）
CREATE OR REPLACE VIEW v_session_details AS
SELECT 
    s.id,
    s.session_id,
    s.agent_id,
    a.agent_name,
    s.title,
    s.created_at,
    s.updated_at,
    COUNT(sl.id) as message_count
FROM sessions s
LEFT JOIN agents a ON s.agent_id = a.agent_id AND a.is_deleted = FALSE
LEFT JOIN session_logs sl ON s.session_id = sl.session_id AND sl.is_deleted = FALSE
WHERE s.is_deleted = FALSE
GROUP BY s.id, s.session_id, s.agent_id, a.agent_name, s.title, s.created_at, s.updated_at;

-- =====================================================
-- 5. 完成信息
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '会话表(sessions)初始化完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建的表:';
    RAISE NOTICE '  - sessions (会话表)';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建的索引:';
    RAISE NOTICE '  - idx_session_agent_id (智能体ID索引)';
    RAISE NOTICE '  - idx_session_session_id (会话ID索引)';
    RAISE NOTICE '  - idx_session_agent_id_session_id (复合索引)';
    RAISE NOTICE '  - idx_sessions_created_at (创建时间索引)';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建的视图:';
    RAISE NOTICE '  - v_active_sessions (活跃会话)';
    RAISE NOTICE '  - v_session_details (会话详情)';
    RAISE NOTICE '========================================';
    RAISE NOTICE '示例数据:';
    RAISE NOTICE '  - 演示会话: session_id=1000000001';
    RAISE NOTICE '  - 测试会话: session_id=1000000002';
    RAISE NOTICE '========================================';
END $$;
