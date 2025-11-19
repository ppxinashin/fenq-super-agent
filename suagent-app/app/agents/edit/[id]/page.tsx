'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Header from '@/components/Header'
import ConfirmModal from '@/components/ConfirmModal'
import MobileOnlyNotice from '@/components/MobileOnlyNotice'
import { FaArrowLeft, FaSave, FaRobot, FaInfoCircle, FaTimes, FaCogs } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import { isMobile } from '@/hooks/useMobileRedirect'
import { AVAILABLE_TOOLS, getToolsList } from '@/utils/availableTools'
import { AgentsAPI, AgentInfo } from '@/api'
import { validateMcpConfig } from '@/utils/mcpValidator'

export default function EditAgentPage() {
  const router = useRouter()
  const params = useParams()
  const agentId = params.id as string
  const [isMobileView, setIsMobileView] = useState(false)
  const [agent, setAgent] = useState<AgentInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    systemPrompt: ''
  })

  const [selectedTools, setSelectedTools] = useState<string[]>([])
  const [mcpEnabled, setMcpEnabled] = useState(false)
  const [mcpConfig, setMcpConfig] = useState('')

  useEffect(() => {
    // 检测移动端
    const checkMobile = () => {
      setIsMobileView(isMobile())
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)

    return () => {
      window.removeEventListener('resize', checkMobile)
    }
  }, [])

  useEffect(() => {
    // 如果是移动端，不加载数据
    if (isMobileView) {
      return
    }

    // 加载智能体数据
    const loadAgentData = async () => {
      try {
        setIsLoading(true)
        const response = await AgentsAPI.getAgentById(agentId)
        
        if (response.code === 200 && response.result) {
          const agentData = response.result
          setAgent(agentData)
          setFormData({
            name: agentData.agent_name,
            description: agentData.description,
            systemPrompt: agentData.system_prompt
          })
          setSelectedTools(agentData.tools || [])
          setMcpEnabled(agentData.mcp_status || false)
          setMcpConfig(agentData.mcp_config || '')
        } else {
          toast.error('智能体不存在')
          router.push('/agents')
        }
      } catch (error: any) {
        console.error('加载智能体数据错误:', error)
        toast.error('加载智能体数据失败')
        router.push('/agents')
      } finally {
        setIsLoading(false)
      }
    }

    loadAgentData()
  }, [agentId, router, isMobileView])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleToolToggle = (toolKey: string) => {
    setSelectedTools(prev => 
      prev.includes(toolKey)
        ? prev.filter(key => key !== toolKey)
        : [...prev, toolKey]
    )
  }

  const handleMcpConfigChange = (value: string) => {
    setMcpConfig(value)
  }

  const handleSave = async () => {
    if (!formData.name.trim() || !formData.description.trim() || !formData.systemPrompt.trim()) {
      toast.error('请填写所有必填字段')
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

    setIsSaving(true)

    try {
      const response = await AgentsAPI.updateAgent({
        agent_id: agentId,
        agent_name: formData.name.trim(),
        description: formData.description.trim(),
        system_prompt: formData.systemPrompt.trim(),
        tools: selectedTools,
        mcp_status: mcpEnabled,
        mcp_config: mcpEnabled && mcpConfig.trim() ? mcpConfig.trim() : '{}'
      })

      if (response.code === 200) {
        toast.success('智能体信息更新成功！')
        router.push('/agents')
      } else {
        toast.error(response.message || '更新智能体失败')
      }
    } catch (error: any) {
      console.error('更新智能体错误:', error)
      toast.error(error.response?.data?.message || '更新智能体失败')
    } finally {
      setIsSaving(false)
    }
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

        {/* 智能体详情信息 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FaInfoCircle className="text-indigo-500 mr-2" />
            智能体详情
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 p-3 rounded-md">
              <span className="text-sm text-gray-500">智能体标识</span>
              <p className="font-medium text-gray-900">{agent.agent_id}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-md">
              <span className="text-sm text-gray-500">创建者</span>
              <p className="font-medium text-gray-900">@{agent.creator_username}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-md">
              <span className="text-sm text-gray-500">创建时间</span>
              <p className="font-medium text-gray-900">{agent.created_at ? new Date(agent.created_at).toLocaleString('zh-CN') : '-'}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-md">
              <span className="text-sm text-gray-500">最后更新</span>
              <p className="font-medium text-gray-900">{agent.updated_by_username ? `@${agent.updated_by_username}` : '-'}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-md col-span-2">
              <span className="text-sm text-gray-500">更新时间</span>
              <p className="font-medium text-gray-900">{agent.updated_at ? new Date(agent.updated_at).toLocaleString('zh-CN') : '-'}</p>
            </div>
          </div>
        </div>

        {/* 表单内容 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="space-y-6">
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
      </div>

      </div>
  )
}