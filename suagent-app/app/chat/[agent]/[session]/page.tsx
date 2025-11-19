'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { FaPaperPlane, FaBrain, FaRobot, FaStop } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import { MuiMarkdown } from 'mui-markdown'
import { Highlight, themes } from 'prism-react-renderer'
import { AgentsAPI, ChatAPI, AgentInfo as AgentInfoType, ChatMessage } from '@/api'
import { generateAgentAvatarGradient, getAgentAvatarText, generateAvatarGradient, getAvatarText } from '@/utils/avatarHelper'
import { useAuth } from '@/contexts/AuthContext'
import { API_BASE_URL } from '@/api/config'

// 检测是否为移动端
const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 1024
}

interface Message {
  id: string
  type: 'user' | 'agent'
  content: string
  timestamp: Date
}

export default function ChatSessionPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const agentId = params.agent as string
  const sessionId = params.session as string

  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isMobileView, setIsMobileView] = useState(false)
  const [agentInfo, setAgentInfo] = useState<AgentInfoType | null>(null)
  const [loadingAgent, setLoadingAgent] = useState(true)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [hasHistory, setHasHistory] = useState(false)
  const [isFirstMessage, setIsFirstMessage] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  
  const username = user?.username || 'User'

  // 加载智能体信息
  useEffect(() => {
    const loadAgentInfo = async () => {
      try {
        setLoadingAgent(true)
        const response = await AgentsAPI.getAgentById(agentId)
        
        if (response.code === 200 && response.result) {
          setAgentInfo(response.result)
        } else {
          toast.error('智能体不存在')
          router.push('/market')
        }
      } catch (error: any) {
        console.error('加载智能体信息失败:', error)
        toast.error('加载智能体信息失败')
        router.push('/market')
      } finally {
        setLoadingAgent(false)
      }
    }

    if (agentId) {
      loadAgentInfo()
    }
  }, [agentId, router])

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

  // 加载历史消息
  useEffect(() => {
    const loadHistory = async () => {
      if (!agentInfo || !sessionId) return

      try {
        setLoadingHistory(true)
        const response = await ChatAPI.getSessionMessages(sessionId)
        
        if (response.code === 200 && response.result) {
          const historyMessages = response.result.messages || []
          
          if (historyMessages.length > 0) {
            // 有历史记录，转换为Message格式
            const convertedMessages: Message[] = historyMessages.map((msg: ChatMessage, index: number) => ({
              id: `history-${index}`,
              type: msg.role === 'user' ? 'user' : 'agent',
              content: msg.content,
              timestamp: new Date(msg.created_at)
            }))
            setMessages(convertedMessages)
            setHasHistory(true)
            setIsFirstMessage(false)
          } else {
            // 没有历史记录，显示欢迎消息
            const welcomeMessage: Message = {
              id: 'welcome',
              type: 'agent',
              content: `你好！我是${agentInfo.agent_name}，${agentInfo.description}。有什么我可以帮助你的吗？`,
              timestamp: new Date()
            }
            setMessages([welcomeMessage])
            setHasHistory(false)
            setIsFirstMessage(true)
          }
        }
      } catch (error: any) {
        console.error('加载历史消息失败:', error)
        // 如果加载失败，显示欢迎消息
        const welcomeMessage: Message = {
          id: 'welcome',
          type: 'agent',
          content: `你好！我是${agentInfo.agent_name}，${agentInfo.description}。有什么我可以帮助你的吗？`,
          timestamp: new Date()
        }
        setMessages([welcomeMessage])
        setHasHistory(false)
        setIsFirstMessage(true)
      } finally {
        setLoadingHistory(false)
      }
    }

    loadHistory()
  }, [agentInfo, sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isStreaming) return

    const userMessageContent = inputMessage.trim()
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userMessageContent,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setIsStreaming(true)

    // 创建AI消息占位符
    const agentMessageId = `agent-${Date.now()}`
    const agentReply: Message = {
      id: agentMessageId,
      type: 'agent',
      content: '',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, agentReply])

    // 调用流式聊天接口
    try {
      const token = sessionStorage.getItem('access_token')
      abortControllerRef.current = new AbortController()

      const url = `${API_BASE_URL}/api/v1/chat?agent_id=${encodeURIComponent(agentId)}&session_id=${encodeURIComponent(sessionId)}&message=${encodeURIComponent(userMessageContent)}`
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/event-stream',
        },
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''
      let buffer = ''

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          
          if (done) {
            break
          }

          // 解码数据块
          buffer += decoder.decode(value, { stream: true })
          
          // 按行分割SSE数据
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // 保留最后不完整的行
          
          for (const line of lines) {
            const trimmedLine = line.trim()
            
            // 跳过空行
            if (!trimmedLine) continue
            
            // 检查是否是结束标记
            if (trimmedLine === 'data: [DONE]') {
              continue
            }
            
            // 解析SSE数据格式: data: {"text": "..."}
            if (trimmedLine.startsWith('data: ')) {
              try {
                const jsonStr = trimmedLine.substring(6) // 移除 "data: " 前缀
                const jsonData = JSON.parse(jsonStr)
                
                // 提取text字段
                if (jsonData.text !== undefined) {
                  accumulatedContent += jsonData.text
                  
                  // 更新消息内容
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === agentMessageId
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    )
                  )
                }
              } catch (parseError) {
                console.error('解析SSE数据失败:', parseError, 'Line:', trimmedLine)
              }
            }
          }
        }
      }

      // 流式输出完成后，如果是第一条消息，自动生成标题
      if (isFirstMessage) {
        try {
          await ChatAPI.generateSessionTitle(sessionId)
          setIsFirstMessage(false)
          
          // 通知父窗口刷新会话列表
          if (window.parent !== window) {
            window.parent.postMessage({ type: 'SESSION_TITLE_UPDATED', sessionId }, '*')
          }
        } catch (error) {
          console.error('生成会话标题失败:', error)
        }
      }

    } catch (error: any) {
      console.error('发送消息失败:', error)
      if (error.name !== 'AbortError') {
        toast.error('发送消息失败，请重试')
        // 移除失败的消息
        setMessages(prev => prev.filter(msg => msg.id !== agentMessageId))
      }
    } finally {
      setIsLoading(false)
      setIsStreaming(false)
      abortControllerRef.current = null
    }
  }

  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsLoading(false)
    setIsStreaming(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // 移动端禁用键盘快捷键，只通过按钮发送
    if (!isMobileView && e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // 自动调整 textarea 高度
  const adjustTextareaHeight = () => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      const scrollHeight = inputRef.current.scrollHeight
      inputRef.current.style.height = Math.min(scrollHeight, 120) + 'px'
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [inputMessage])

  // 清理abort controller
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
        abortControllerRef.current = null
      }
    }
  }, [])

  // 加载状态
  if (loadingAgent || !agentInfo || loadingHistory) {
    return (
      <div className="h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            {loadingAgent ? '加载智能体信息...' : loadingHistory ? '加载聊天记录...' : '加载中...'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-white flex flex-col">
      {/* 移动端顶部导航 */}
      {isMobileView && (
        <div className="h-16 border-b border-gray-200 flex items-center justify-between px-4 bg-white">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => router.back()}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div className="flex items-center space-x-2">
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
                style={{
                  background: generateAgentAvatarGradient(agentInfo.agent_id)
                }}
              >
                {getAgentAvatarText(agentInfo.agent_name)}
              </div>
              <h2 className="text-lg font-semibold text-gray-900">{agentInfo.agent_name}</h2>
            </div>
          </div>
        </div>
      )}

      {/* 消息展示区 */}
      <div className="flex-1 overflow-y-auto px-4 py-6 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className={`${isMobileView ? 'max-w-lg' : 'max-w-4xl'} mx-auto space-y-4 ${isMobileView ? 'pt-8' : ''}`}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
              message.type === 'user' ? 'justify-end' : ''
            }`}
          >
            {message.type === 'agent' && (
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white text-xs font-bold"
                style={{
                  background: generateAgentAvatarGradient(agentInfo.agent_id)
                }}
              >
                {getAgentAvatarText(agentInfo.agent_name)}
              </div>
            )}
              <div
                className={`max-w-2xl px-4 py-3 rounded-2xl shadow-sm ${
                  message.type === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-800 border border-gray-200'
                }`}
              >
                {message.type === 'user' ? (
                  <p className="whitespace-pre-wrap break-words">{message.content}</p>
                ) : (
                  <MuiMarkdown
                    overrides={{
                      a: {
                        component: 'a',
                        props: {
                          target: '_blank',
                          rel: 'noopener noreferrer',
                          style: { color: '#4f46e5', textDecoration: 'underline' }
                        },
                      },
                      h1: {
                        component: 'h1',
                        props: {
                          style: { 
                            fontSize: '1.875rem', 
                            fontWeight: 'bold', 
                            marginTop: '1.5rem', 
                            marginBottom: '1rem',
                            color: '#1f2937'
                          }
                        },
                      },
                      h2: {
                        component: 'h2',
                        props: {
                          style: { 
                            fontSize: '1.5rem', 
                            fontWeight: 'bold', 
                            marginTop: '1.25rem', 
                            marginBottom: '0.75rem',
                            color: '#1f2937'
                          }
                        },
                      },
                      h3: {
                        component: 'h3',
                        props: {
                          style: { 
                            fontSize: '1.25rem', 
                            fontWeight: 'bold', 
                            marginTop: '1rem', 
                            marginBottom: '0.5rem',
                            color: '#1f2937'
                          }
                        },
                      },
                      p: {
                        component: 'p',
                        props: {
                          style: { 
                            marginBottom: '0.75rem',
                            lineHeight: '1.6',
                            color: '#374151'
                          }
                        },
                      },
                      ul: {
                        component: 'ul',
                        props: {
                          style: { 
                            marginBottom: '0.75rem',
                            paddingLeft: '1.5rem',
                            color: '#374151'
                          }
                        },
                      },
                      ol: {
                        component: 'ol',
                        props: {
                          style: { 
                            marginBottom: '0.75rem',
                            paddingLeft: '1.5rem',
                            color: '#374151'
                          }
                        },
                      },
                      li: {
                        component: 'li',
                        props: {
                          style: { 
                            marginBottom: '0.25rem',
                            lineHeight: '1.6'
                          }
                        },
                      },
                      blockquote: {
                        component: 'blockquote',
                        props: {
                          style: { 
                            borderLeft: '4px solid #4f46e5',
                            paddingLeft: '1rem',
                            margin: '1rem 0',
                            fontStyle: 'italic',
                            color: '#6b7280'
                          }
                        },
                      },
                      table: {
                        component: 'table',
                        props: {
                          style: { 
                            width: '100%',
                            borderCollapse: 'collapse',
                            marginBottom: '1rem'
                          }
                        },
                      },
                      th: {
                        component: 'th',
                        props: {
                          style: { 
                            border: '1px solid #e5e7eb',
                            padding: '0.5rem',
                            textAlign: 'left',
                            backgroundColor: '#f9fafb',
                            fontWeight: 'bold'
                          }
                        },
                      },
                      td: {
                        component: 'td',
                        props: {
                          style: { 
                            border: '1px solid #e5e7eb',
                            padding: '0.5rem',
                            textAlign: 'left'
                          }
                        },
                      },
                      code: {
                        component: 'code',
                        props: {
                          style: { 
                            backgroundColor: '#f3f4f6',
                            padding: '0.125rem 0.25rem',
                            borderRadius: '0.25rem',
                            fontSize: '0.875rem',
                            color: '#d1d5db'
                          }
                        },
                      },
                    }}
                    Highlight={Highlight}
                    themes={themes}
                    prismTheme={themes.github}
                  >
                    {message.content}
                  </MuiMarkdown>
                )}
              </div>
              {message.type === 'user' && (
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold text-xs"
                  style={{
                    background: generateAvatarGradient(username),
                    textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                  }}
                >
                  {getAvatarText(username)}
                </div>
              )}
            </div>
          ))}

          {/* 加载状态 */}
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white text-xs font-bold"
                style={{
                  background: generateAgentAvatarGradient(agentInfo.agent_id)
                }}
              >
                {getAgentAvatarText(agentInfo.agent_name)}
              </div>
              <div className="bg-gray-100 text-gray-800 border border-gray-200 px-4 py-3 rounded-2xl shadow-sm">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span className="text-sm text-gray-500">正在思考...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 输入区域 */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-4">
        <div className={`${isMobileView ? 'max-w-lg' : 'max-w-4xl'} mx-auto`}>
          {/* 移动端简化输入 */}
          {isMobileView ? (
            <div className="flex gap-3">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="请输入消息..."
                disabled={isLoading}
                rows={1}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none bg-white self-end"
                style={{
                  minHeight: '48px',
                  maxHeight: '120px',
                  resize: 'none',
                  overflow: 'auto'
                }}
              />
              {isStreaming ? (
                <button
                  onClick={handleStopStreaming}
                  className="w-12 h-12 bg-red-600 text-white rounded-lg flex items-center justify-center hover:bg-red-700 transition-colors duration-200 flex-shrink-0"
                >
                  <FaStop />
                </button>
              ) : (
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="w-12 h-12 bg-indigo-600 text-white rounded-lg flex items-center justify-center hover:bg-indigo-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                >
                  <FaPaperPlane />
                </button>
              )}
            </div>
          ) : (
            /* 桌面端完整输入区域 */
            <div>
              <div className="flex gap-3">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="请输入消息..."
                  disabled={isLoading}
                  rows={1}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none bg-white self-end"
                  style={{
                    minHeight: '48px',
                    maxHeight: '120px',
                    resize: 'none',
                    overflow: 'auto'
                  }}
                />
                {isStreaming ? (
                  <button
                    onClick={handleStopStreaming}
                    className="w-12 h-12 bg-red-600 text-white rounded-lg flex items-center justify-center hover:bg-red-700 transition-colors duration-200 flex-shrink-0"
                  >
                    <FaStop />
                  </button>
                ) : (
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="w-12 h-12 bg-indigo-600 text-white rounded-lg flex items-center justify-center hover:bg-indigo-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                  >
                    <FaPaperPlane />
                  </button>
                )}
              </div>

              {/* 快捷键提示 - 仅桌面端显示 */}
              <div className="mt-2 text-center">
                <p className="text-sm text-gray-500">
                  按 Enter 发送消息 • 按 Shift + Enter 换行
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}