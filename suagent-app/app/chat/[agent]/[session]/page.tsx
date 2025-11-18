'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { FaPaperPlane, FaBrain, FaRobot, FaStop } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

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
    welcomeMessage: '我是Java架构师，一位全能的资深Java技术专家'
  },
  debug: {
    id: 'debug',
    name: '代码 Debug',
    description: '能助您分析代码、优化性能',
    color: 'from-blue-400 to-purple-500',
    welcomeMessage: '我是代码Debug，能助您分析代码、优化性能'
  },
  python: {
    id: 'python',
    name: 'Python专家',
    description: '一位精通 Python3 的问题解决专家',
    color: 'from-green-400 to-blue-500',
    welcomeMessage: '我是Python专家，一位精通Python3的问题解决专家'
  },
  linux: {
    id: 'linux',
    name: 'Linux系统',
    description: 'Linux操作系统与应用专家',
    color: 'from-gray-400 to-black',
    welcomeMessage: '我是Linux系统，Linux操作系统与应用专家'
  },
  translate: {
    id: 'translate',
    name: '技术翻译助手',
    description: '精通技术文档中英翻译',
    color: 'from-purple-400 to-pink-500',
    welcomeMessage: '我是技术翻译助手，精通技术文档中英翻译'
  },
  patent: {
    id: 'patent',
    name: '专利技术交底书',
    description: '专业辅助撰写专利交底书',
    color: 'from-yellow-400 to-orange-500',
    welcomeMessage: '我是专利技术交底书，专业辅助撰写专利交底书'
  },
  work: {
    id: 'work',
    name: '工作处理助手',
    description: '解决各类工作难题，优化流程',
    color: 'from-teal-400 to-green-500',
    welcomeMessage: '我是工作处理助手，解决各类工作难题，优化流程'
  },
  report: {
    id: 'report',
    name: '工作成果汇报',
    description: '撰写客观全面的绩效自评',
    color: 'from-indigo-400 to-blue-500',
    welcomeMessage: '我是工作成果汇报，撰写客观全面的绩效自评'
  }
}

export default function ChatSessionPage() {
  const params = useParams()
  const router = useRouter()
  const agentId = params.agent as string
  const sessionId = params.session as string

  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isMobileView, setIsMobileView] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const streamingRef = useRef<NodeJS.Timeout | null>(null)

  const agentInfo = agentConfigs[agentId]

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
    if (!agentInfo) {
      toast.error('智能体不存在')
      return
    }

    // 添加欢迎消息
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'agent',
      content: agentInfo.welcomeMessage,
      timestamp: new Date()
    }
    setMessages([welcomeMessage])
  }, [agentId, agentInfo])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setIsStreaming(true)

    // 模拟AI流式回复
    const agentMessageId = (Date.now() + 1).toString()
    const agentReply: Message = {
      id: agentMessageId,
      type: 'agent',
      content: '',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, agentReply])

    // 模拟流式输出
    const fullContent = `感谢你的提问！关于"${userMessage.content}"，我需要为你提供详细的解答。

## 分析要点

让我为你分析一下这个问题：

1. **核心概念理解**
   - 这是一个关于 **${userMessage.content}** 的问题
   - 需要从多个角度进行思考

2. **解决方案**
   \`\`\`javascript
   // 示例代码
   function solveProblem(input) {
     return input.map(item => process(item));
   }
   \`\`\`

3. **重要提示**
   - 注意事项 ⚠️
   - 最佳实践 ✅

> 💡 **建议**: 如果需要更详细的解释，请随时提问！`

    const chunks = fullContent.split(' ')
    let currentContent = ''
    let chunkIndex = 0

    streamingRef.current = setInterval(() => {
      if (chunkIndex < chunks.length) {
        currentContent += (chunkIndex > 0 ? ' ' : '') + chunks[chunkIndex]
        setMessages(prev =>
          prev.map(msg =>
            msg.id === agentMessageId
              ? { ...msg, content: currentContent }
              : msg
          )
        )
        chunkIndex++
      } else {
        if (streamingRef.current) {
          clearInterval(streamingRef.current)
          streamingRef.current = null
        }
        setIsLoading(false)
        setIsStreaming(false)
      }
    }, 50)
  }

  const handleStopStreaming = () => {
    if (streamingRef.current) {
      clearInterval(streamingRef.current)
      streamingRef.current = null
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

  // 清理定时器
  useEffect(() => {
    return () => {
      if (streamingRef.current) {
        clearInterval(streamingRef.current)
        streamingRef.current = null
      }
    }
  }, [])

  if (!agentInfo) {
    return null
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
              <div className={`w-8 h-8 bg-gradient-to-r ${agentInfo.color} rounded-full flex items-center justify-center`}>
                <FaRobot className="text-white text-sm" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">{agentInfo.name}</h2>
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
                <div className={`w-8 h-8 bg-gradient-to-r ${agentInfo.color} rounded-full flex items-center justify-center flex-shrink-0`}>
                  <FaRobot className="text-white text-sm" />
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
                  <div className="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-code:text-pink-600 prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-blockquote:border-l-indigo-500 prose-blockquote:text-gray-600 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-ol:text-gray-700">
                    <Markdown remarkPlugins={[remarkGfm]}>{message.content}</Markdown>
                  </div>
                )}
              </div>
              {message.type === 'user' && (
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <FaBrain className="text-white text-sm" />
                </div>
              )}
            </div>
          ))}

          {/* 加载状态 */}
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className={`w-8 h-8 bg-gradient-to-r ${agentInfo.color} rounded-full flex items-center justify-center flex-shrink-0`}>
                <FaRobot className="text-white text-sm" />
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