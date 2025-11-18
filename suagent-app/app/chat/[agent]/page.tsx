'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import Header from '@/components/Header'
import ConfirmModal from '@/components/ConfirmModal'
import { FaRobot, FaPlus, FaTrash, FaDatabase, FaComments, FaArrowLeft, FaPaperPlane } from 'react-icons/fa'
import { toast } from 'react-hot-toast'

// 检测是否为移动端
const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 1024
}

interface Conversation {
  id: string
  title: string
  timestamp: string
  agentId: string
}

interface AgentInfo {
  id: string
  name: string
  description: string
  color: string
  welcomeMessage: string
}

const agentConfigs: Record<string, AgentInfo> = {
  java: {
    id: 'java',
    name: 'Java架构师',
    description: '一位全能的资深 Java 技术专家',
    color: 'from-orange-400 to-red-500',
    welcomeMessage: '你好！我是Java架构师，我是一位全能的资深Java技术专家，专注于企业级应用架构设计、微服务架构、性能优化等领域。我可以帮助你解决各种Java技术难题。'
  },
  debug: {
    id: 'debug',
    name: '代码 Debug',
    description: '能助您分析代码、优化性能',
    color: 'from-blue-400 to-purple-500',
    welcomeMessage: '你好！我是代码Debug专家，我可以帮助你分析代码、优化性能、解答编程疑问。有什么问题需要我协助解决吗？'
  },
  python: {
    id: 'python',
    name: 'Python专家',
    description: '一位精通 Python3 的问题解决专家',
    color: 'from-green-400 to-blue-500',
    welcomeMessage: '你好！我是Python专家，精通Python3和各类Python框架。无论是数据分析、机器学习还是Web开发，我都能为你提供专业的帮助。'
  },
  linux: {
    id: 'linux',
    name: 'Linux系统',
    description: 'Linux操作系统与应用专家',
    color: 'from-gray-400 to-black',
    welcomeMessage: '你好！我是Linux系统专家，可以帮助你学习Linux操作系统与应用，从基础命令到高级系统管理，我都能为你提供指导。'
  },
  translate: {
    id: 'translate',
    name: '技术翻译助手',
    description: '精通技术文档中英翻译',
    color: 'from-purple-400 to-pink-500',
    welcomeMessage: '你好！我是技术翻译助手，精通技术文档的中英翻译与写作，可以为你提供专业的翻译服务。'
  },
  patent: {
    id: 'patent',
    name: '专利技术交底书',
    description: '专业辅助撰写专利交底书',
    color: 'from-yellow-400 to-orange-500',
    welcomeMessage: '你好！我是专利技术交底书专家，可以专业辅助你撰写专利交底书，确保高效精准，遵循流程规范。'
  },
  work: {
    id: 'work',
    name: '工作处理助手',
    description: '解决各类工作难题，优化流程',
    color: 'from-teal-400 to-green-500',
    welcomeMessage: '你好！我是工作处理助手，可以帮助你解决各类工作难题，优化工作流程，提高工作效率。'
  },
  report: {
    id: 'report',
    name: '工作成果汇报',
    description: '撰写客观全面的绩效自评',
    color: 'from-indigo-400 to-blue-500',
    welcomeMessage: '你好！我是工作成果汇报专家，可以为你撰写客观全面的绩效自评，分点展示你的工作详情和成果。'
  }
}

export default function ChatFrameworkPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const agentId = params.agent as string
  const sessionIdFromUrl = searchParams.get('session')
  const initialSessionId = params.session as string
  const [activePanel, setActivePanel] = useState<'chat' | 'knowledge'>('chat')
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      title: '如何设计高并发订单系统？',
      timestamp: '刚刚',
      agentId: 'java'
    },
    {
      id: '2',
      title: 'Spring Boot多数据源配置',
      timestamp: '昨天',
      agentId: 'java'
    }
  ])

  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null)

  const agentInfo = agentConfigs[agentId]

  useEffect(() => {
    if (!agentInfo) {
      toast.error('智能体不存在')
      router.push('/market')
      return
    }

    // 如果URL中有session参数，设置为当前session
    if (sessionIdFromUrl || initialSessionId) {
      const sessionId = sessionIdFromUrl || initialSessionId
      setCurrentSessionId(sessionId)
      setActivePanel('chat')
    }

    // 监听浏览器后退/前进事件
    const handlePopState = () => {
      const urlParams = new URLSearchParams(window.location.search)
      const sessionFromUrl = urlParams.get('session')

      if (sessionFromUrl) {
        setCurrentSessionId(sessionFromUrl)
        setActivePanel('chat')
      } else {
        const pathSegments = window.location.pathname.split('/')
        const sessionFromPath = pathSegments[pathSegments.length - 1]

        if (sessionFromPath && sessionFromPath !== agentId && !isNaN(Number(sessionFromPath))) {
          setCurrentSessionId(sessionFromPath)
          setActivePanel('chat')
        } else {
          setCurrentSessionId(null)
        }
      }
    }

    window.addEventListener('popstate', handlePopState)

    return () => {
      window.removeEventListener('popstate', handlePopState)
    }
  }, [agentId, agentInfo, router, sessionIdFromUrl, initialSessionId])

  const handleNewConversation = () => {
    const newId = Date.now().toString()
    const newConversation: Conversation = {
      id: newId,
      title: '新对话',
      timestamp: '刚刚',
      agentId: agentId
    }

    setConversations(prev => [newConversation, ...prev])
    // 更新URL但不跳转
    const url = new URL(window.location.href)
    url.searchParams.set('session', newId)
    window.history.pushState({}, '', url.toString())
    // 设置当前session并切换到对话面板
    setCurrentSessionId(newId)
    setActivePanel('chat')
    toast.success('新对话已创建')
  }

  const handleSelectConversation = (conversationId: string) => {
    // 更新URL但不跳转，只是改变地址栏
    const url = new URL(window.location.href)
    url.searchParams.set('session', conversationId)
    window.history.pushState({}, '', url.toString())
    // 设置当前session并切换到对话面板
    setCurrentSessionId(conversationId)
    setActivePanel('chat')
  }

  const handleDeleteConversation = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setConversationToDelete(conversationId)
    setShowDeleteModal(true)
  }

  const confirmDeleteConversation = () => {
    if (conversationToDelete) {
      setConversations(prev => prev.filter(conv => conv.id !== conversationToDelete))
      toast.success('对话已删除')
      setConversationToDelete(null)
    }
    setShowDeleteModal(false)
  }

  const cancelDeleteConversation = () => {
    setConversationToDelete(null)
    setShowDeleteModal(false)
  }

  const handleSwitchToChat = () => {
    setActivePanel('chat')
  }

  const handleSwitchToKnowledge = () => {
    setActivePanel('knowledge')
  }

  const handleBackToMarket = () => {
    router.push('/market')
  }

  if (!agentInfo) {
    return null
  }

  // 桌面端渲染（移动端会自动重定向到聊天会话页面）
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header/>

      <div className="flex flex-1 overflow-hidden" style={{ height: 'calc(100vh - 64px)' }}>
        {/* 左侧边栏 */}
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
          {/* 智能体信息 */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`w-12 h-12 bg-gradient-to-r ${agentInfo.color} rounded-full flex items-center justify-center`}>
                  <FaRobot className="text-white text-xl" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{agentInfo.name}</h3>
                  <p className="text-xs text-gray-500">作者</p>
                </div>
              </div>
              <button
                onClick={handleBackToMarket}
                className="text-gray-400 hover:text-gray-600"
              >
                <FaArrowLeft />
              </button>
            </div>

            <button
              onClick={handleNewConversation}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition-colors duration-300 flex items-center justify-center space-x-2"
            >
              <FaPlus />
              <span>新建对话</span>
            </button>
          </div>

          {/* 功能菜单 */}
          <div className="p-4 border-b border-gray-200">
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-3">功能菜单</h4>
            <div className="space-y-1">
              <button
                onClick={handleSwitchToChat}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                  activePanel === 'chat'
                    ? 'bg-indigo-50 text-indigo-600 font-medium'
                    : 'hover:bg-gray-100'
                }`}
              >
                <FaComments className="text-lg" />
                <span>对话</span>
              </button>
              <button
                onClick={handleSwitchToKnowledge}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                  activePanel === 'knowledge'
                    ? 'bg-indigo-50 text-indigo-600 font-medium'
                    : 'hover:bg-gray-100'
                }`}
              >
                <FaDatabase className="text-lg" />
                <span>知识库</span>
              </button>
            </div>
          </div>

          {/* 历史会话 */}
          <div className="flex-1 overflow-y-auto p-4">
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-3">历史会话</h4>
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => handleSelectConversation(conversation.id)}
                  className="group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:shadow-sm"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{conversation.title}</p>
                    <p className="text-xs text-gray-500">{conversation.timestamp}</p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(conversation.id, e)}
                    className="text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <FaTrash className="text-sm" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 主内容区域 */}
        <div className="flex-1 flex flex-col">
          {/* 顶部导航 */}
          <div className="h-16 border-b border-gray-200 flex items-center justify-between px-6 bg-white">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {activePanel === 'chat' ? agentInfo.name : '知识库管理'}
              </h2>
            </div>
            <div className="flex items-center space-x-4">
            </div>
          </div>

          {/* 聊天内容区域 */}
          {activePanel === 'chat' && (
            <div className="flex-1 overflow-hidden h-full">
              {/* 如果有session ID，显示嵌入的对话页面 */}
              {currentSessionId ? (
                <iframe
                  src={`/chat/${agentId}/${currentSessionId}`}
                  className="w-full h-full border-0"
                />
              ) : (
                /* 提示页面 */
                <div className="w-full h-full bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
                  <div className="text-center max-w-lg mx-auto px-8">
                    <div className={`w-24 h-24 bg-gradient-to-r ${agentInfo.color} rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg`}>
                      <FaRobot className="text-white text-4xl" />
                    </div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">
                      与{agentInfo.name}开始对话
                    </h2>
                    <p className="text-gray-600 text-lg mb-8 max-w-md">
                      点击左侧的"新建对话"按钮，开始与智能体进行对话交流
                    </p>
                    <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200">
                      <div className="flex items-center justify-center space-x-3 text-gray-600">
                        <FaPlus className="text-xl" />
                        <span className="text-base">点击"新建对话"开始聊天</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 知识库面板 */}
          {activePanel === 'knowledge' && (
            <div className="flex-1 overflow-hidden">
              <iframe
                src={`/chat/${agentId}/knowledge`}
                className="w-full h-full border-0"
                style={{ minHeight: '600px' }}
              />
            </div>
          )}
        </div>
      </div>

      {/* 删除对话确认模态框 */}
      <ConfirmModal
        isOpen={showDeleteModal}
        title="删除对话"
        message="确定要删除这个对话吗？"
        confirmText="删除"
        cancelText="取消"
        type="danger"
        onConfirm={confirmDeleteConversation}
        onCancel={cancelDeleteConversation}
      />
    </div>
  )
}