'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import ConfirmModal from '@/components/ConfirmModal'
import { FaArrowLeft, FaPlus, FaInfoCircle, FaCommentDots, FaCogs, FaCheck, FaEye, FaEyeSlash, FaTimes, FaQuestionCircle, FaRobot, FaSpinner } from 'react-icons/fa'
import { toast } from 'react-hot-toast'

interface ToolConfig {
  id: string
  name: string
  description: string
  enabled: boolean
}


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

  const [tools, setTools] = useState<ToolConfig[]>([
    { id: 'web_search', name: '网页搜索', description: '获取实时网络信息', enabled: true },
    { id: 'calculator', name: '计算器', description: '进行数学计算', enabled: true },
    { id: 'code_execution', name: '代码执行', description: '运行代码片段', enabled: false },
    { id: 'file_processing', name: '文件处理', description: '读取和处理文件', enabled: false },
    { id: 'image_generation', name: '图片生成', description: '根据描述生成图片', enabled: false },
    { id: 'speech_to_text', name: '语音转文字', description: '处理语音输入', enabled: false }
  ])

  
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

  const handleToolToggle = (toolId: string) => {
    setTools(prev => prev.map(tool =>
      tool.id === toolId ? { ...tool, enabled: !tool.enabled } : tool
    ))
  }

  const handleCreateAgent = () => {
    if (!agentName.trim() || !agentId.trim() || !agentDescription.trim() || !systemPrompt.trim()) {
      toast.error('请填写所有必填字段')
      return
    }

    if (!/^[a-zA-Z0-9_]+$/.test(agentId)) {
      toast.error('智能体标识只能包含字母、数字和下划线')
      return
    }

    setIsCreating(true)

    setTimeout(() => {
      setIsCreating(false)
      setShowSuccessModal(true)
      toast.success('智能体创建成功！')
    }, 2000)
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
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header/>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1">
        {/* 页面标题 */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => router.back()}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <FaArrowLeft className="text-xl" />
            </button>
          </div>
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">创建 AI 智能体</h2>
            <p className="text-gray-600">配置你的专属智能助手，定制其功能和行为</p>
          </div>
        </div>

        {/* 智能体图标预览 */}
        <div className="flex justify-center mb-8">
          <div className="w-24 h-24 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center">
            <span className="text-white text-4xl font-bold">{getAgentIconPreview()}</span>
          </div>
        </div>

        <form className="space-y-6">
          {/* 基本信息 */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <FaInfoCircle className="text-indigo-500 mr-3" />
              基本信息
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                <p className="text-xs text-gray-500 mt-1">智能体的唯一标识，只能包含字母、数字和下划线</p>
              </div>

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
            </div>

            <div className="mt-6">
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
          </div>

          {/* 系统提示词 */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <FaCommentDots className="text-indigo-500 mr-3" />
              系统提示词
            </h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                设定描述 <span className="text-red-500">*</span> <span className="px-2 py-1 bg-indigo-100 text-indigo-600 rounded-full text-xs font-medium">重要</span>
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
          </div>

          {/* 高级设置 */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <FaCogs className="text-indigo-500 mr-3" />
              高级设置
            </h3>

            <div className="space-y-6">
              {/* 工具绑定区域 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">工具绑定</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-60 overflow-y-auto pr-2">
                  {tools.map((tool) => (
                    <label
                      key={tool.id}
                      className={`flex items-center p-3 border rounded-xl cursor-pointer transition-all duration-300 ${
                        tool.enabled ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={tool.enabled}
                        onChange={() => handleToolToggle(tool.id)}
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

          {/* 创建按钮 */}
          <div className="text-center">
            <button
              type="button"
              onClick={handleCreateAgent}
              disabled={isCreating}
              className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-base hover:from-indigo-600 hover:to-purple-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-0.5 hover:shadow-lg"
            >
              {isCreating ? (
                <>
                  <FaSpinner className="inline mr-2 animate-spin" />
                  创建中...
                </>
              ) : (
                <>
                  <FaPlus className="inline mr-2" />
                  创建智能体
                </>
              )}
            </button>
          </div>
        </form>
      </main>

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