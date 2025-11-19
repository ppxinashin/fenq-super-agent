'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import Header from '@/components/Header'
import ConfirmModal from '@/components/ConfirmModal'
import { FaRobot, FaPlus, FaTrash, FaDatabase, FaComments, FaArrowLeft, FaPaperPlane, FaEdit, FaCheck, FaTimes } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import { AgentsAPI, ChatAPI, AgentInfo as AgentInfoType, SessionInfoResponse } from '@/api'
import { generateAgentAvatarGradient, getAgentAvatarText } from '@/utils/avatarHelper'

// 检测是否为移动端
const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 1024
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
  const [agentInfo, setAgentInfo] = useState<AgentInfoType | null>(null)
  const [loading, setLoading] = useState(true)
  const [conversations, setConversations] = useState<SessionInfoResponse[]>([])
  const [loadingSessions, setLoadingSessions] = useState(false)

  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null)
  
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')

  // 加载会话列表（最多20条）
  const loadSessions = async () => {
    try {
      setLoadingSessions(true)
      const response = await ChatAPI.getSessions({
        agent_id: agentId,
        page: 1,
        page_size: 20
      })
      
      if (response.code === 200 && response.result) {
        setConversations(response.result.data || [])
      } else {
        console.error('加载会话列表失败:', response.message)
      }
    } catch (error: any) {
      console.error('加载会话列表错误:', error)
    } finally {
      setLoadingSessions(false)
    }
  }

  // 加载智能体信息
  useEffect(() => {
    const loadAgentInfo = async () => {
      try {
        setLoading(true)
        const response = await AgentsAPI.getAgentById(agentId)
        
        if (response.code === 200 && response.result) {
          setAgentInfo(response.result)
          // 加载完智能体信息后，加载会话列表
          loadSessions()
        } else {
          toast.error('智能体不存在')
          router.push('/market')
        }
      } catch (error: any) {
        console.error('加载智能体信息失败:', error)
        toast.error('加载智能体信息失败')
        router.push('/market')
      } finally {
        setLoading(false)
      }
    }

    if (agentId) {
      loadAgentInfo()
    }
  }, [agentId, router])

  useEffect(() => {
    if (!agentInfo) {
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

    // 监听来自iframe的消息（标题更新通知）
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'SESSION_TITLE_UPDATED') {
        // 重新加载会话列表以获取更新的标题
        loadSessions()
      }
    }

    window.addEventListener('popstate', handlePopState)
    window.addEventListener('message', handleMessage)

    return () => {
      window.removeEventListener('popstate', handlePopState)
      window.removeEventListener('message', handleMessage)
    }
  }, [agentId, agentInfo, router, sessionIdFromUrl, initialSessionId])

  const handleNewConversation = async () => {
    try {
      toast.loading('正在创建新对话...', { id: 'new-conversation' })
      
      // 调用API创建会话
      const response = await ChatAPI.createSession({ agent_id: agentId })
      
      if (response.code === 200 && response.result) {
        const sessionId = response.result.session_id
        
        // 重新加载会话列表
        await loadSessions()
        
        // 更新URL但不跳转
        const url = new URL(window.location.href)
        url.searchParams.set('session', sessionId)
        window.history.pushState({}, '', url.toString())
        
        // 设置当前session并切换到对话面板
        setCurrentSessionId(sessionId)
        setActivePanel('chat')
        
        toast.success('新对话已创建', { id: 'new-conversation' })
      } else {
        toast.error(response.message || '创建对话失败', { id: 'new-conversation' })
      }
    } catch (error: any) {
      console.error('创建对话失败:', error)
      toast.error(error.response?.data?.message || '创建对话失败', { id: 'new-conversation' })
    }
  }

  const handleSelectConversation = (sessionId: string) => {
    // 更新URL但不跳转，只是改变地址栏
    const url = new URL(window.location.href)
    url.searchParams.set('session', sessionId)
    window.history.pushState({}, '', url.toString())
    // 设置当前session并切换到对话面板
    setCurrentSessionId(sessionId)
    setActivePanel('chat')
  }

  const handleDeleteConversation = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setConversationToDelete(sessionId)
    setShowDeleteModal(true)
  }

  const confirmDeleteConversation = async () => {
    if (conversationToDelete) {
      try {
        const response = await ChatAPI.deleteSession(conversationToDelete)
        
        if (response.code === 200) {
          // 如果删除的是当前会话，清空当前会话ID
          if (currentSessionId === conversationToDelete) {
            setCurrentSessionId(null)
            const url = new URL(window.location.href)
            url.searchParams.delete('session')
            window.history.pushState({}, '', url.toString())
          }
          
          // 重新加载会话列表
          await loadSessions()
          toast.success('对话已删除')
        } else {
          toast.error(response.message || '删除对话失败')
        }
      } catch (error: any) {
        console.error('删除对话失败:', error)
        toast.error(error.response?.data?.message || '删除对话失败')
      }
      setConversationToDelete(null)
    }
    setShowDeleteModal(false)
  }

  const cancelDeleteConversation = () => {
    setConversationToDelete(null)
    setShowDeleteModal(false)
  }

  const handleStartEditTitle = (sessionId: string, currentTitle: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingSessionId(sessionId)
    setEditingTitle(currentTitle || '')
  }

  const handleSaveTitle = async (sessionId: string) => {
    if (!editingTitle.trim()) {
      toast.error('标题不能为空')
      return
    }

    try {
      const response = await ChatAPI.updateSessionTitle(sessionId, { title: editingTitle.trim() })
      
      if (response.code === 200) {
        // 重新加载会话列表
        await loadSessions()
        toast.success('标题已更新')
      } else {
        toast.error(response.message || '更新标题失败')
      }
    } catch (error: any) {
      console.error('更新标题失败:', error)
      toast.error(error.response?.data?.message || '更新标题失败')
    }
    
    setEditingSessionId(null)
    setEditingTitle('')
  }

  const handleCancelEdit = () => {
    setEditingSessionId(null)
    setEditingTitle('')
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

  // 格式化时间戳
  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return '刚刚'
    if (diffMins < 60) return `${diffMins}分钟前`
    if (diffHours < 24) return `${diffHours}小时前`
    if (diffDays < 7) return `${diffDays}天前`
    
    // 超过7天显示具体日期
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }

  // 加载状态
  if (loading || !agentInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header/>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">加载中...</p>
          </div>
        </div>
      </div>
    )
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
                <div 
                  className="w-12 h-12 rounded-full flex items-center justify-center text-white text-lg font-bold"
                  style={{
                    background: generateAgentAvatarGradient(agentInfo.agent_id)
                  }}
                >
                  {getAgentAvatarText(agentInfo.agent_name)}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{agentInfo.agent_name}</h3>
                  <p className="text-xs text-gray-500">@{agentInfo.creator_username}</p>
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
          <div className="h-96 overflow-y-auto p-4 bg-white">
            {loadingSessions ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
              </div>
            ) : conversations.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-sm">
                暂无会话记录
              </div>
            ) : (
              <div className="space-y-2 pr-2">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.session_id}
                    onClick={() => editingSessionId !== conversation.session_id && handleSelectConversation(conversation.session_id)}
                    className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:shadow-sm ${
                      currentSessionId === conversation.session_id ? 'bg-indigo-50 border-indigo-200 border' : ''
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      {editingSessionId === conversation.session_id ? (
                        <div className="flex items-center space-x-2" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="text"
                            value={editingTitle}
                            onChange={(e) => setEditingTitle(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSaveTitle(conversation.session_id)}
                            className="flex-1 px-2 py-1 text-sm border border-indigo-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            autoFocus
                          />
                          <button
                            onClick={() => handleSaveTitle(conversation.session_id)}
                            className="text-green-600 hover:text-green-700"
                          >
                            <FaCheck />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="text-red-600 hover:text-red-700"
                          >
                            <FaTimes />
                          </button>
                        </div>
                      ) : (
                        <>
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {conversation.title || '<无标题>'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatTimestamp(conversation.last_message_at || conversation.created_at)}
                          </p>
                        </>
                      )}
                    </div>
                    {editingSessionId !== conversation.session_id && (
                      <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={(e) => handleStartEditTitle(conversation.session_id, conversation.title, e)}
                          className="text-gray-400 hover:text-indigo-600 p-1"
                          title="编辑标题"
                        >
                          <FaEdit className="text-sm" />
                        </button>
                        <button
                          onClick={(e) => handleDeleteConversation(conversation.session_id, e)}
                          className="text-gray-400 hover:text-red-600 p-1"
                          title="删除会话"
                        >
                          <FaTrash className="text-sm" />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 主内容区域 */}
        <div className="flex-1 flex flex-col">
          {/* 顶部导航 */}
          <div className="h-16 border-b border-gray-200 flex items-center justify-between px-6 bg-white">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {activePanel === 'chat' ? agentInfo.agent_name : '知识库管理'}
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
                    <div 
                      className="w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg text-white text-4xl font-bold"
                      style={{
                        background: generateAgentAvatarGradient(agentInfo.agent_id)
                      }}
                    >
                      {getAgentAvatarText(agentInfo.agent_name)}
                    </div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">
                      与{agentInfo.agent_name}开始对话
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