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

interface Agent {
  id: number
  agentId: string
  name: string
  description: string
  createdBy: string
  createdAt: string
  updatedBy: string
  updatedAt: string
}

export default function AgentsPage() {
  const router = useRouter()
  const [isMobileView, setIsMobileView] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [pageSize, setPageSize] = useState(10)
  const [currentPage, setCurrentPage] = useState(1)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [agentToDelete, setAgentToDelete] = useState<number | null>(null)

  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 1,
      agentId: 'customer_service',
      name: '客服助手',
      description: '专业的在线客服智能助手，提供24小时服务支持',
      createdBy: 'admin',
      createdAt: '2024-01-20 10:30:00',
      updatedBy: 'admin',
      updatedAt: '2024-02-15 14:20:00'
    },
    {
      id: 2,
      agentId: 'data_analyst',
      name: '数据分析专家',
      description: '专业的数据分析智能助手，提供数据洞察和报告生成',
      createdBy: 'user123',
      createdAt: '2024-02-10 09:15:00',
      updatedBy: 'user123',
      updatedAt: '2024-02-20 16:45:00'
    },
    {
      id: 3,
      agentId: 'knowledge_base',
      name: '知识库助手',
      description: '企业知识库管理智能助手，提供知识检索和问答服务',
      createdBy: 'moderator',
      createdAt: '2024-03-05 11:45:00',
      updatedBy: 'admin',
      updatedAt: '2024-03-10 10:15:00'
    }
  ])

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

  // 如果是移动端，显示限制页面
  if (isMobileView) {
    return <MobileOnlyNotice />
  }

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const paginatedAgents = filteredAgents.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const totalPages = Math.ceil(filteredAgents.length / pageSize)

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleEditAgent = (agentId: number) => {
    router.push(`/agents/edit/${agentId}`)
  }

  const handleDeleteAgent = (agentId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setAgentToDelete(agentId)
    setShowDeleteModal(true)
  }

  const confirmDeleteAgent = () => {
    if (agentToDelete) {
      setAgents(prev => prev.filter(agent => agent.id !== agentToDelete))
      toast.success('智能体删除成功')
      setAgentToDelete(null)
    }
    setShowDeleteModal(false)
  }

  const cancelDeleteAgent = () => {
    setAgentToDelete(null)
    setShowDeleteModal(false)
  }

  const getAgentIcon = (agentId: string) => {
    switch (agentId) {
      case 'customer_service':
        return FaComments
      case 'data_analyst':
        return FaBullseye
      case 'knowledge_base':
        return FaBook
      default:
        return FaRobot
    }
  }

  const getAgentIconColor = (agentId: string) => {
    switch (agentId) {
      case 'customer_service':
        return 'bg-blue-100 text-blue-600'
      case 'data_analyst':
        return 'bg-green-100 text-green-600'
      case 'knowledge_base':
        return 'bg-purple-100 text-purple-600'
      default:
        return 'bg-gray-100 text-gray-600'
    }
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
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="搜索智能体"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-4 pr-12 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      className="absolute right-2 top-1.5 p-1.5 text-gray-400 hover:text-purple-600 transition-colors duration-200"
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
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">更新人</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">更新时间</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedAgents.map((agent, index) => {
                    const Icon = getAgentIcon(agent.agentId)
                    const iconColorClass = getAgentIconColor(agent.agentId)

                    return (
                      <tr
                        key={agent.id}
                        className="hover:bg-gray-50 transition-all duration-300 hover:shadow-md"
                      >
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{agent.id}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{agent.agentId}</td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center space-x-3">
                            <div className={`w-8 h-8 ${iconColorClass.split(' ')[0]} rounded-full flex items-center justify-center transform transition-transform duration-300 hover:scale-110`}>
                              <Icon className={`text-sm ${iconColorClass.split(' ')[1]}`} />
                            </div>
                            <span className="text-sm font-medium text-gray-900 hover:text-purple-600 transition-colors duration-200">{agent.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">{agent.description}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{agent.createdBy}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{agent.createdAt}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{agent.updatedBy}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{agent.updatedAt}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleEditAgent(agent.id)}
                            className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 px-2 py-1 rounded mr-2 transition-all duration-200"
                          >
                            <FaEdit className="inline mr-1" /> 编辑
                          </button>
                          <button
                            onClick={(e) => handleDeleteAgent(agent.id, e)}
                            className="text-red-600 hover:text-red-900 hover:bg-red-50 px-2 py-1 rounded transition-all duration-200"
                          >
                            <FaTrash className="inline mr-1" /> 删除
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* 分页 */}
            <div className="px-6 py-4 border-t border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-500">
                  显示 {(currentPage - 1) * pageSize + 1} 到 {Math.min(currentPage * pageSize, filteredAgents.length)} 条，共 {filteredAgents.length} 条记录
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