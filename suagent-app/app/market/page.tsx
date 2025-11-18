'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { FaSearch, FaSpinner } from 'react-icons/fa'
import Footer from '@/components/Footer'
import { toast } from 'react-hot-toast'
import AuthProtected from '@/components/AuthProtected'
import { AgentsAPI } from '../../api'
import { AgentSimpleInfo } from '../../api'
import { generateAgentAvatarGradient, getAgentAvatarText } from '../../utils/avatarHelper'

// 检测是否为移动端
const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 1024
}

export default function MarketPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [agents, setAgents] = useState<AgentSimpleInfo[]>([])
  const [displayAgents, setDisplayAgents] = useState<AgentSimpleInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [hasMore, setHasMore] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const router = useRouter()

  // 加载智能体数据
  const loadAgents = async (page: number = 1, keyword: string = '', append: boolean = false) => {
    try {
      setLoading(true)
      console.log('正在加载智能体...', { page, keyword, append })

      const response = await AgentsAPI.getAgentCardList({
        page,
        page_size: 8, // 一次最多只展示8个智能体
        keyword
      })

      console.log('API响应:', response)

      if (response.code === 200 && response.result) {
        const newAgents = response.result.data || []
        console.log('获取到的智能体数量:', newAgents.length)
        console.log('智能体数据:', newAgents)

        if (append) {
          setAgents(prev => [...prev, ...newAgents])
          setDisplayAgents(prev => [...prev, ...newAgents])
        } else {
          setAgents(newAgents)
          setDisplayAgents(newAgents)
        }

        // 检查是否还有更多数据
        setHasMore(newAgents.length === 8 && response.result.total > page * 8)
        setCurrentPage(page)

        if (newAgents.length === 0) {
          console.log('没有找到智能体数据')
        }
      } else {
        console.error('API返回错误:', response)
        toast.error(response.message || '加载智能体失败')
      }
    } catch (error: any) {
      console.error('加载智能体错误:', error)
      const errorMessage = error.response?.data?.message || error.message || '加载智能体失败'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
      setInitialLoading(false)
    }
  }

  // 初始化加载
  useEffect(() => {
    loadAgents()
  }, [])

  // 搜索处理
  useEffect(() => {
    if (currentPage === 1) {
      const timeoutId = setTimeout(() => {
        loadAgents(1, searchTerm, false)
      }, 300) // 300ms 防抖
      return () => clearTimeout(timeoutId)
    }
  }, [searchTerm])

  // 搜索智能体
  const handleSearch = () => {
    setCurrentPage(1)
    loadAgents(1, searchTerm, false)
  }

  // 处理智能体点击
  const handleAgentClick = (agentId: string, agentName: string) => {
    toast.success(`正在加载 ${agentName}...`)

    if (isMobile()) {
      // 移动端：直接创建新session并跳转到聊天页面
      const sessionId = Date.now().toString()
      setTimeout(() => {
        router.push(`/chat/${agentId}/${sessionId}`)
      }, 300)
    } else {
      // 桌面端：跳转到智能体框架页面
      setTimeout(() => {
        router.push(`/chat/${agentId}`)
      }, 500)
    }
  }

  // 加载更多
  const handleLoadMore = () => {
    if (hasMore && !loading) {
      loadAgents(currentPage + 1, searchTerm, true)
    }
  }

  // 格式化日期
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 1) return '昨天'
    if (diffDays < 7) return `${diffDays}天前`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}个月前`
    return `${Math.floor(diffDays / 365)}年前`
  }

  return (
    <AuthProtected>
      <div className="min-h-screen bg-gray-50">
        <Header/>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 页面标题 */}
          <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">发现 AI 智能体</h2>
            <p className="text-gray-600">探索丰富的智能体生态，找到适合你的AI助手</p>
          </div>

          {/* 搜索框 */}
          <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
            <div className="max-w-2xl">
              <div className="flex shadow-lg rounded-lg overflow-hidden">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <FaSearch className="text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="w-full pl-10 pr-4 py-3 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-inset-0"
                    placeholder="搜索智能体..."
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="px-6 py-3 bg-indigo-600 text-white hover:bg-indigo-700 transition-colors duration-200 flex items-center focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-inset-0 disabled:opacity-50"
                >
                  <FaSearch className="mr-2" />
                  搜索
                </button>
              </div>
            </div>
          </div>

          {/* 智能体网格 */}
          {initialLoading ? (
            <div className="flex items-center justify-center py-12">
              <FaSpinner className="animate-spin text-4xl text-indigo-600 mr-3" />
              <span className="text-lg text-gray-600">加载智能体中...</span>
            </div>
          ) : displayAgents.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-lg mb-2">暂无智能体</div>
              <p className="text-gray-500">
                {searchTerm ? '没有找到匹配的智能体，请尝试其他关键词' : '还没有智能体，快去创建一个吧！'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {displayAgents.map((agent, index) => (
                <div
                  key={agent.agent_id}
                  onClick={() => handleAgentClick(agent.agent_id, agent.agent_name)}
                  className="bg-white rounded-xl border border-gray-200 hover:shadow-xl hover:-translate-y-2 transition-all duration-300 cursor-pointer group flex flex-col h-full"
                >
                  <div className="p-6 flex flex-col h-full">
                    {/* 智能体头像 */}
                    <div
                      className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 text-white text-2xl font-bold group-hover:scale-110 transition-transform duration-300"
                      style={{
                        background: generateAgentAvatarGradient(agent.agent_id)
                      }}
                    >
                      {getAgentAvatarText(agent.agent_name)}
                    </div>

                    {/* 标题和描述 */}
                    <div className="flex-grow">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors line-clamp-1">
                        {agent.agent_name}
                      </h3>
                      <p className="text-gray-600 text-sm line-clamp-2 overflow-hidden">
                        {agent.description}
                      </p>
                    </div>

                    {/* 底部信息 - 固定在底部 */}
                    <div className="flex items-center justify-between text-xs text-gray-500 mt-4 pt-4 border-t border-gray-100">
                      <span className="truncate flex-1 mr-2">@{agent.creator_username}</span>
                      <span className="whitespace-nowrap">{formatDate(agent.created_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 加载更多 */}
          {!initialLoading && hasMore && (
            <div className="mt-12 text-center">
              <button
                onClick={handleLoadMore}
                disabled={loading}
                className="px-8 py-3 border border-gray-300 rounded-xl text-gray-600 hover:bg-gray-50 hover:border-gray-400 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center mx-auto space-x-2"
              >
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin" />
                    <span>加载中...</span>
                  </>
                ) : (
                  <>
                    <FaSpinner />
                    <span>加载更多</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* 显示总数信息 */}
          {!initialLoading && agents.length > 0 && (
            <div className="mt-8 text-center text-sm text-gray-500">
              已显示 {Math.min(agents.length, 8)} 个智能体
            </div>
          )}
        </main>

        <Footer />
      </div>
    </AuthProtected>
  )
}