'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import ConfirmModal from '@/components/ConfirmModal'
import { FaArrowLeft, FaPlus, FaInfoCircle, FaCommentDots, FaCogs, FaCheck, FaEye, FaEyeSlash, FaTimes, FaQuestionCircle, FaRobot, FaSpinner } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import { AVAILABLE_TOOLS, getToolsList } from '@/utils/availableTools'
import { AgentsAPI } from '@/api'
import { validateMcpConfig } from '@/utils/mcpValidator'


export default function CreateAgentPage() {
  const router = useRouter()
  const [agentName, setAgentName] = useState('我的智能助手')
  const [agentId, setAgentId] = useState('my_agent')
  const [agentDescription, setAgentDescription] = useState('一个功能强大的AI助手')
  const [systemPrompt, setSystemPrompt] = useState('你是一个智能AI助手，具备强大的语言理解和生成能力。你能够帮助用户解决各种问题，提供有用的信息和建议。请以友好、专业的态度与用户交流。')
  const [mcpEnabled, setMcpEnabled] = useState(false)
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showLogoutModal, setShowLogoutModal] = useState(false)
  const [longTermMemory, setLongTermMemory] = useState(false)
  const [isCreating, setIsCreating] = useState(false)

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const [mcpConfig, setMcpConfig] = useState('')
  const [selectedTools, setSelectedTools] = useState<string[]>([]) // 选中的工具键名数组

  
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('#userAvatar') && !target.closest('#userMenu')) {
        setShowUserMenu(false)
      }
    }

    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  const handleToolToggle = (toolKey: string) => {
    setSelectedTools(prev => 
      prev.includes(toolKey)
        ? prev.filter(key => key !== toolKey)
        : [...prev, toolKey]
    )
  }

  const handleCreateAgent = async () => {
    if (!agentName.trim() || !agentId.trim() || !agentDescription.trim() || !systemPrompt.trim()) {
      toast.error('请填写所有必填字段')
      return
    }

    if (!/^[a-zA-Z0-9_]+$/.test(agentId)) {
      toast.error('智能体标识只能包含字母、数字和下划线')
      return
    }

    if (agentId.toLowerCase() === 'memory') {
      toast.error('智能体标识不能命名为 memory')
      return
    }

    // 验证MCP配置格式
    if (mcpEnabled && mcpConfig.trim() && mcpConfig.trim() !== '{}') {
      const validation = validateMcpConfig(mcpConfig)
      if (!validation.valid) {
        toast.error(`MCP配置格式错误: ${validation.error}`)
        return
      }
    }

    setIsCreating(true)

    try {
      const response = await AgentsAPI.createAgent({
        agent_id: agentId.trim(),
        agent_name: agentName.trim(),
        description: agentDescription.trim(),
        system_prompt: systemPrompt.trim(),
        tools: selectedTools,
        mcp_status: mcpEnabled,
        mcp_config: mcpEnabled && mcpConfig.trim() ? mcpConfig.trim() : '{}'
      })

      if (response.code === 200) {
        setShowSuccessModal(true)
        toast.success('智能体创建成功！')
      } else {
        toast.error(response.message || '创建智能体失败')
      }
    } catch (error: any) {
      console.error('创建智能体错误:', error)
      toast.error(error.response?.data?.message || '创建智能体失败')
    } finally {
      setIsCreating(false)
    }
  }

  const handleGoToChat = () => {
    setShowSuccessModal(false)
    router.push('/market')
  }

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault()

    if (newPassword !== confirmPassword) {
      toast.error('新密码和确认密码不一致！')
      return
    }

    if (newPassword.length < 6) {
      toast.error('新密码长度至少为6位！')
      return
    }

    toast.success('密码修改成功！')
    setShowChangePasswordModal(false)
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
  }

  const handleLogout = () => {
    setShowLogoutModal(true)
  }

  const confirmLogout = () => {
    setShowLogoutModal(false)
    router.push('/')
  }

  const cancelLogout = () => {
    setShowLogoutModal(false)
  }

  const getAgentIconPreview = () => {
    return agentName.trim().charAt(0) || '智'
  }

  const handleMcpConfigChange = (value: string) => {
    setMcpConfig(value)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header/>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 页面标题和返回按钮 */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.back()}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <FaArrowLeft className="text-xl" />
            </button>
            <h1 className="text-3xl font-bold text-gray-900">创建智能体</h1>
          </div>
          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={handleCreateAgent}
              disabled={isCreating}
              className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isCreating ? (
                <>
                  <FaSpinner className="animate-spin" />
                  <span>创建中...</span>
                </>
              ) : (
                <>
                  <FaPlus />
                  <span>创建</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* 表单内容 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="space-y-6">
            {/* 智能体标识 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                智能体标识 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="请输入智能体标识"
                required
              />
              <p className="text-xs text-gray-500 mt-1">智能体的唯一标识，只能包含字母、数字和下划线，不能命名为 memory</p>
            </div>

            {/* 智能体名称 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                智能体名称 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={agentName}
                onChange={(e) => setAgentName(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="请输入智能体名称"
                required
              />
              <p className="text-xs text-gray-500 mt-1">智能体的显示名称，将在市场中展示</p>
            </div>

            {/* 智能体介绍 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                智能体介绍 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={agentDescription}
                onChange={(e) => setAgentDescription(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="请简要描述智能体的功能"
                required
              />
              <p className="text-xs text-gray-500 mt-1">简要介绍智能体的主要功能和特点</p>
            </div>

            {/* 系统提示词 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                系统提示词 <span className="text-red-500">*</span>
              </label>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                rows={6}
                placeholder="请输入系统提示词，定义智能体的行为模式和能力范围..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">定义智能体的角色、能力和行为准则，这将影响智能体的回答风格和能力范围</p>
            </div>

            {/* 工具绑定 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4">工具绑定</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-60 overflow-y-auto pr-2">
                {getToolsList().map((tool) => (
                  <label
                    key={tool.key}
                    className={`flex items-center p-3 border rounded-xl cursor-pointer transition-all duration-300 ${
                      selectedTools.includes(tool.key) ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-300'
                    }`}
                  >
                    <input
                      type="checkbox"
                      value={tool.key}
                      checked={selectedTools.includes(tool.key)}
                      onChange={() => handleToolToggle(tool.key)}
                      className="mr-3 w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                    />
                    <div>
                      <div className="font-medium text-gray-900">{tool.name}</div>
                      <div className="text-xs text-gray-600">{tool.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* MCP开关 */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  启用 MCP
                </label>
              </div>

              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={mcpEnabled}
                  onChange={(e) => setMcpEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            {/* MCP配置区域 */}
            {mcpEnabled && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">MCP 服务器配置</label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-sm"
                  rows={8}
                  value={mcpConfig}
                  onChange={(e) => handleMcpConfigChange(e.target.value)}
                  placeholder={`{
  "suagent-youtube-mcp": {
    "type": "sse",
    "url": "http://127.0.0.1:10086/sse"
  },
  "amap-maps": {
    "type": "sse",
    "url": "https://mcp.api-inference.modelscope.net/xxxx/sse"
  }
}`}
                />
                <p className="text-xs text-gray-500 mt-1">配置自定义模型服务的连接信息，可与系统工具同时使用</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 成功提示模态框 */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FaCheck className="text-green-600 text-2xl" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">创建成功！</h3>
              <p className="text-gray-600 mb-6">你的智能体已成功创建，即将跳转到对话界面</p>
              <button
                onClick={handleGoToChat}
                className="px-8 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors duration-300"
              >
                开始使用
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 修改密码模态框 */}
      {showChangePasswordModal && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">修改密码</h3>
              <button
                onClick={() => setShowChangePasswordModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <FaTimes className="text-lg" />
              </button>
            </div>

            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">当前密码</label>
                <div className="relative">
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="请输入当前密码"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  >
                    {showCurrentPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">新密码</label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="请输入新密码"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  >
                    {showNewPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">确认新密码</label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="请再次输入新密码"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowChangePasswordModal(false)}
                  className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  确认修改
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 退出登录确认模态框 */}
      <ConfirmModal
        isOpen={showLogoutModal}
        title="退出登录"
        message="确定要退出登录吗？"
        confirmText="退出"
        cancelText="取消"
        type="warning"
        onConfirm={confirmLogout}
        onCancel={cancelLogout}
      />
    </div>
  )
}