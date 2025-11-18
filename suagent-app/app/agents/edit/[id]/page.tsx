'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Header from '@/components/Header'
import ConfirmModal from '@/components/ConfirmModal'
import MobileOnlyNotice from '@/components/MobileOnlyNotice'
import { FaArrowLeft, FaSave, FaRobot, FaInfoCircle, FaTimes, FaCogs } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import { isMobile } from '@/hooks/useMobileRedirect'

interface Agent {
  id: number
  agentId: string
  name: string
  description: string
  systemPrompt: string
  createdBy: string
  createdAt: string
  updatedBy: string
  updatedAt: string
}

interface ToolConfig {
  id: string
  name: string
  description: string
  enabled: boolean
}

const mockAgents: Agent[] = [
  {
    id: 1,
    agentId: 'customer_service',
    name: '客服助手',
    description: '专业的在线客服智能助手，提供24小时服务支持',
    systemPrompt: '你是一个专业的在线客服助手，具备良好的沟通能力和服务意识。能够耐心解答用户问题，提供专业的产品咨询和服务支持。请以友好、专业的态度与用户交流。',
    createdBy: 'admin',
    createdAt: '2024-01-20 10:30:00',
    updatedBy: 'admin',
    updatedAt: '2024-02-15 14:20:00'
  },
  {
    id: 2,
    agentId: 'data_analyst',
    name: '数据分析师',
    description: '专业的数据分析智能助手，擅长数据处理和可视化',
    systemPrompt: '你是一个专业的数据分析师，精通数据处理、统计分析和数据可视化。能够帮助用户进行数据清洗、统计分析、制作图表等工作。请以专业、严谨的态度为用户提供数据分析服务。',
    createdBy: 'admin',
    createdAt: '2024-01-21 09:15:00',
    updatedBy: 'admin',
    updatedAt: '2024-02-10 16:45:00'
  },
  {
    id: 3,
    agentId: 'content_creator',
    name: '内容创作者',
    description: '创意内容生成助手，擅长文案创作和创意写作',
    systemPrompt: '你是一个创意内容创作者，擅长各类文案写作、创意构思和内容策划。能够根据用户需求创作高质量的营销文案、产品描述、社交媒体内容等。请以创意、专业的态度提供内容创作服务。',
    createdBy: 'moderator',
    createdAt: '2024-01-22 11:20:00',
    updatedBy: 'admin',
    updatedAt: '2024-02-05 10:30:00'
  }
]

export default function EditAgentPage() {
  const router = useRouter()
  const params = useParams()
  const agentId = params.id as string
  const [isMobileView, setIsMobileView] = useState(false)
  const [agent, setAgent] = useState<Agent | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    systemPrompt: ''
  })

  const [tools, setTools] = useState<ToolConfig[]>([
    { id: 'web_search', name: '网页搜索', description: '获取实时网络信息', enabled: true },
    { id: 'calculator', name: '计算器', description: '进行数学计算', enabled: true },
    { id: 'code_execution', name: '代码执行', description: '运行代码片段', enabled: false },
    { id: 'file_processing', name: '文件处理', description: '读取和处理文件', enabled: false },
    { id: 'image_generation', name: '图片生成', description: '根据描述生成图片', enabled: false },
    { id: 'speech_to_text', name: '语音转文字', description: '处理语音输入', enabled: false }
  ])

  const [mcpEnabled, setMcpEnabled] = useState(false)
  const [mcpConfig, setMcpConfig] = useState('')

  useEffect(() => {
    // 检测移动端
    const checkMobile = () => {
      setIsMobileView(isMobile())
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)

    // 如果是移动端，显示限制页面
    if (isMobile()) {
      return
    }

    // 加载智能体数据
    const foundAgent = mockAgents.find(a => a.id.toString() === agentId)
    if (foundAgent) {
      setAgent(foundAgent)
      setFormData({
        name: foundAgent.name,
        description: foundAgent.description,
        systemPrompt: foundAgent.systemPrompt
      })
    } else {
      toast.error('智能体不存在')
      router.push('/agents')
    }

    setIsLoading(false)

    return () => {
      window.removeEventListener('resize', checkMobile)
    }
  }, [agentId, router])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleToolToggle = (toolId: string) => {
    setTools(prev => prev.map(tool =>
      tool.id === toolId ? { ...tool, enabled: !tool.enabled } : tool
    ))
  }

  const handleMcpConfigChange = (value: string) => {
    setMcpConfig(value)
  }

  const handleSave = () => {
    if (!formData.name.trim() || !formData.description.trim() || !formData.systemPrompt.trim()) {
      toast.error('请填写所有必填字段')
      return
    }

    setIsSaving(true)

    setTimeout(() => {
      setIsSaving(false)
      toast.success('智能体信息更新成功！')
      router.push('/agents')
    }, 2000)
  }

  // 如果是移动端，显示限制页面
  if (isMobileView) {
    return <MobileOnlyNotice />
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <FaRobot className="text-6xl text-gray-300 mb-4 mx-auto animate-pulse" />
          <p className="text-gray-500">正在加载智能体信息...</p>
        </div>
      </div>
    )
  }

  if (!agent) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

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
            <h1 className="text-3xl font-bold text-gray-900">编辑智能体</h1>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FaSave />
              <span>{isSaving ? '保存中...' : '保存'}</span>
            </button>
          </div>
        </div>

        {/* 表单内容 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="space-y-6">
            {/* 智能体标识（只读） */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                智能体标识 <span className="text-gray-500 text-xs">(不可修改)</span>
              </label>
              <input
                type="text"
                value={agent.agentId}
                disabled
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-500 cursor-not-allowed"
                readOnly
              />
            </div>

            {/* 智能体名称 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                智能体名称 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="请输入智能体名称"
                required
              />
            </div>

            {/* 智能体描述 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                智能体描述 <span className="text-red-500">*</span>
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                placeholder="请输入智能体描述"
                required
              />
            </div>

            {/* 系统提示词 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                系统提示词 <span className="text-red-500">*</span>
              </label>
              <textarea
                name="systemPrompt"
                value={formData.systemPrompt}
                onChange={handleInputChange}
                rows={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none font-mono text-sm"
                placeholder="请输入系统提示词，定义智能体的行为和角色"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                <FaInfoCircle className="inline mr-1" />
                系统提示词用于定义智能体的行为模式、知识范围和交互方式
              </p>
            </div>
          </div>

          {/* 高级设置 */}
          <div className="mt-8 pt-6 border-t border-gray-200">
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

          {/* 基本信息 */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-6 text-sm">
              <div>
                <span className="text-gray-500">创建者：</span>
                <span className="text-gray-900 ml-2">{agent.createdBy}</span>
              </div>
              <div>
                <span className="text-gray-500">创建时间：</span>
                <span className="text-gray-900 ml-2">{agent.createdAt}</span>
              </div>
              <div>
                <span className="text-gray-500">最后更新：</span>
                <span className="text-gray-900 ml-2">{agent.updatedBy}</span>
              </div>
              <div>
                <span className="text-gray-500">更新时间：</span>
                <span className="text-gray-900 ml-2">{agent.updatedAt}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      </div>
  )
}