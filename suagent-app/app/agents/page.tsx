'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import MobileOnlyNotice from '@/components/MobileOnlyNotice'
import ConfirmModal from '@/components/ConfirmModal'
import { FaRobot, FaEdit, FaTrash, FaSearch, FaPlus, FaComments, FaBullseye, FaBook, FaChevronLeft, FaChevronRight } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import { isMobile } from '@/hooks/useMobileRedirect'
import { AgentsAPI, AgentListItem } from '@/api'
import { generateAgentAvatarGradient, getAgentAvatarText } from '@/utils/avatarHelper'

export default function AgentsPage() {
  const router = useRouter()
  const [isMobileView, setIsMobileView] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [pageSize, setPageSize] = useState(10)
  const [currentPage, setCurrentPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [agents, setAgents] = useState<AgentListItem[]>([])

  // 加载智能体列表
  const loadAgents = async (page: number = currentPage, keyword: string = searchTerm) => {
    try {
      setLoading(true)
      const params: any = {
        page,
        page_size: pageSize
      }
      
      if (keyword) {
        params.keyword = keyword
      }

      const response = await AgentsAPI.getAgentManagementList(params)

      if (response.code === 200 && response.result) {
        setAgents(response.result.data || [])
        setTotal(response.result.total || 0)
        setCurrentPage(response.result.page || page)
      } else {
        toast.error(response.message || '加载智能体列表失败')
      }
    } catch (error: any) {
      console.error('加载智能体列表错误:', error)
      toast.error(error.response?.data?.message || '加载智能体列表失败')
    } finally {
      setLoading(false)
    }
  }

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
    if (!isMobileView) {
      loadAgents(1, '')
    }
  }, [isMobileView])

  // 如果是移动端，显示限制页面
  if (isMobileView) {
    return <MobileOnlyNotice />
  }

  const totalPages = Math.ceil(total / pageSize)

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setCurrentPage(1)
    loadAgents(1, searchTerm)
  }

  const handlePageChange = (page: number) => {
    loadAgents(page, searchTerm)
  }

  const handleSearch = () => {
    setSearchTerm(searchInput)
    loadAgents(1, searchInput)
  }

  const handleEditAgent = (agentId: string) => {
    router.push(`/agents/edit/${agentId}`)
  }

  const handleDeleteAgent = (agentId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setAgentToDelete(agentId)
    setShowDeleteModal(true)
  }

  const confirmDeleteAgent = async () => {
    if (agentToDelete) {
      try {
        const response = await AgentsAPI.deleteAgent(agentToDelete)
        
        if (response.code === 200) {
          toast.success('智能体删除成功')
          await loadAgents(currentPage, searchTerm)
        } else {
          toast.error(response.message || '删除智能体失败')
        }
      } catch (error: any) {
        console.error('删除智能体错误:', error)
        toast.error(error.response?.data?.message || '删除智能体失败')
      }
      setAgentToDelete(null)
    }
    setShowDeleteModal(false)
  }

  const cancelDeleteAgent = () => {
    setAgentToDelete(null)
    setShowDeleteModal(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 页面标题 */}
          <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h1 className="text-2xl font-bold text-gray-900">智能体管理</h1>
            <p className="text-gray-600 mt-1">管理AI智能体配置和设置</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* 工具栏 */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-stretch shadow-sm rounded-lg overflow-hidden">
                    <input
                      type="text"
                      placeholder="搜索智能体"
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                      className="pl-4 pr-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400 focus:shadow-lg transition-all duration-200 w-64 h-[38px] border-0"
                    />
                    <button
                      type="button"
                      onClick={handleSearch}
                      className="px-4 bg-white text-gray-600 hover:text-purple-600 hover:bg-gray-50 transition-all duration-200 h-[38px] flex items-center justify-center border-l border-gray-200"
                    >
                      <FaSearch />
                    </button>
                  </div>
                </div>
                <button
                  onClick={() => router.push('/agents/create')}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors duration-200 flex items-center"
                >
                  <FaPlus className="mr-2" />
                  创建智能体
                </button>
              </div>
            </div>

            {/* 页面大小选择 */}
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  每页显示
                </div>
                <select
                  value={pageSize}
                  onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value={10}>10 条</option>
                  <option value={15}>15 条</option>
                  <option value={20}>20 条</option>
                </select>
              </div>
            </div>

            {/* 智能体表格 */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">智能体ID</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">智能体名称</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">智能体介绍</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建人</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">更新时间</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={8} className="px-4 py-8 text-center">
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mr-3"></div>
                          <span className="text-gray-600">加载中...</span>
                        </div>
                      </td>
                    </tr>
                  ) : agents.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                        {searchTerm ? '没有找到匹配的智能体' : '暂无智能体数据'}
                      </td>
                    </tr>
                  ) : (
                    agents.map((agent, index) => (
                      <tr
                        key={agent.agent_id}
                        className="hover:bg-gray-50 transition-all duration-300 hover:shadow-md"
                      >
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{(currentPage - 1) * pageSize + index + 1}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{agent.agent_id}</td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center space-x-3">
                            <div 
                              className="w-8 h-8 rounded-full flex items-center justify-center transform transition-transform duration-300 hover:scale-110 text-white text-xs font-bold"
                              style={{ background: generateAgentAvatarGradient(agent.agent_id) }}
                            >
                              {getAgentAvatarText(agent.agent_name)}
                            </div>
                            <span className="text-sm font-medium text-gray-900 hover:text-purple-600 transition-colors duration-200">{agent.agent_name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">{agent.description}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{agent.creator_username}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{agent.created_at ? new Date(agent.created_at).toLocaleString('zh-CN') : '-'}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{agent.updated_at ? new Date(agent.updated_at).toLocaleString('zh-CN') : '-'}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleEditAgent(agent.agent_id)}
                            className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 px-2 py-1 rounded mr-2 transition-all duration-200"
                          >
                            <FaEdit className="inline mr-1" /> 编辑
                          </button>
                          <button
                            onClick={(e) => handleDeleteAgent(agent.agent_id, e)}
                            className="text-red-600 hover:text-red-900 hover:bg-red-50 px-2 py-1 rounded transition-all duration-200"
                          >
                            <FaTrash className="inline mr-1" /> 删除
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* 分页 */}
            <div className="px-6 py-4 border-t border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-500">
                  显示 {total > 0 ? (currentPage - 1) * pageSize + 1 : 0} 到 {Math.min(currentPage * pageSize, total)} 条，共 {total} 条记录
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 text-gray-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:disabled:bg-transparent"
                  >
                    <FaChevronLeft className="text-xs" />
                  </button>
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    const page = i + 1
                    return (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`px-3 py-1 rounded transition-all duration-200 ${
                          currentPage === page
                            ? 'bg-purple-600 text-white'
                            : 'border border-gray-300 hover:bg-gray-50 text-gray-700'
                        }`}
                      >
                        {page}
                      </button>
                    )
                  })}
                  {totalPages > 5 && <span className="text-gray-500">...</span>}
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 text-gray-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:disabled:bg-transparent"
                  >
                    <FaChevronRight className="text-xs" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />

      {/* 删除智能体确认模态框 */}
      <ConfirmModal
        isOpen={showDeleteModal}
        title="删除智能体"
        message="确定要删除这个智能体吗？"
        confirmText="删除"
        cancelText="取消"
        type="danger"
        onConfirm={confirmDeleteAgent}
        onCancel={cancelDeleteAgent}
      />
    </div>
  )
}