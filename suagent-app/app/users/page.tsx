'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import ConfirmModal from '@/components/ConfirmModal'
import MobileOnlyNotice from '@/components/MobileOnlyNotice'
import { FaUsers, FaCog, FaEdit, FaTrash, FaSearch, FaPlus, FaTimes, FaUser, FaBullseye } from 'react-icons/fa'
import { toast } from 'react-hot-toast'
import { isMobile } from '@/hooks/useMobileRedirect'

interface User {
  id: number
  username: string
  role: 'admin' | 'user'
  createdAt: string
}

export default function UserManagementPage() {
  const router = useRouter()
  const [isMobileView, setIsMobileView] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [pageSize, setPageSize] = useState(10)
  const [currentPage, setCurrentPage] = useState(1)

  const [users, setUsers] = useState<User[]>([
    { id: 1, username: 'admin', role: 'admin', createdAt: '2024-01-15 09:30:00' },
    { id: 2, username: 'user123', role: 'user', createdAt: '2024-02-20 14:15:00' }
  ])

  const [newUser, setNewUser] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    role: 'user' as 'admin' | 'user'
  })

  const [editUser, setEditUser] = useState({
    username: '',
    role: 'user' as 'admin' | 'user',
    password: '',
    confirmPassword: ''
  })

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

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const paginatedUsers = filteredUsers.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const totalPages = Math.ceil(filteredUsers.length / pageSize)

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault()

    if (!newUser.username.trim() || !newUser.password.trim() || !newUser.confirmPassword.trim()) {
      toast.error('请填写所有必填字段')
      return
    }

    if (newUser.username.length < 3 || newUser.username.length > 20) {
      toast.error('用户名长度必须在3-20个字符之间')
      return
    }

    if (!/^[a-zA-Z0-9_]+$/.test(newUser.username)) {
      toast.error('用户名只能包含字母、数字和下划线')
      return
    }

    if (newUser.password.includes(' ')) {
      toast.error('密码不能包含空格')
      return
    }

    if (newUser.password.length < 8 || newUser.password.length > 20) {
      toast.error('密码长度必须为8-20个字符')
      return
    }

    if (newUser.password !== newUser.confirmPassword) {
      toast.error('两次输入的密码不一致')
      return
    }

    const existingUser = users.find(u => u.username === newUser.username)
    if (existingUser) {
      toast.error('用户名已存在')
      return
    }

    const user: User = {
      id: Math.max(...users.map(u => u.id)) + 1,
      username: newUser.username,
      role: newUser.role,
      createdAt: new Date().toISOString().replace('T', ' ').slice(0, 19)
    }

    setUsers([...users, user])
    setNewUser({ username: '', password: '', confirmPassword: '', role: 'user' })
    setShowCreateModal(false)
    toast.success('用户创建成功')
  }

  const handleEditUser = (e: React.FormEvent) => {
    e.preventDefault()

    if (!editUser.password.trim()) {
      toast.error('密码不能为空')
      return
    }

    if (!editUser.confirmPassword.trim()) {
      toast.error('请确认密码')
      return
    }

    if (editUser.password.includes(' ')) {
      toast.error('密码不能包含空格')
      return
    }

    if (editUser.password.length < 8 || editUser.password.length > 20) {
      toast.error('密码长度必须为8-20个字符')
      return
    }

    if (editUser.password !== editUser.confirmPassword) {
      toast.error('两次输入的密码不一致')
      return
    }

    if (!selectedUser) return

    setUsers(users.map(user =>
      user.id === selectedUser.id
        ? { ...user, role: editUser.role }
        : user
    ))

    setShowEditModal(false)
    setSelectedUser(null)
    toast.success('用户信息更新成功')
  }

  const handleDeleteUser = () => {
    if (!selectedUser) return

    if (selectedUser.username === 'admin') {
      toast.error('不能删除管理员账户')
      return
    }

    setUsers(users.filter(user => user.id !== selectedUser.id))
    setShowDeleteModal(false)
    setSelectedUser(null)
    toast.success('用户删除成功')
  }

  const openEditModal = (user: User) => {
    setSelectedUser(user)
    setEditUser({ username: user.username, role: user.role, password: '', confirmPassword: '' })
    setShowEditModal(true)
  }

  const openDeleteModal = (user: User) => {
    setSelectedUser(user)
    setShowDeleteModal(true)
  }

  const getRoleBadge = (role: string) => {
    return role === 'admin' ? (
      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">管理员</span>
    ) : (
      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">用户</span>
    )
  }

  const getAvatarColor = (role: string) => {
    return role === 'admin' ? 'bg-blue-100' : 'bg-green-100'
  }

  const getAvatarTextColor = (role: string) => {
    return role === 'admin' ? 'text-blue-600' : 'text-green-600'
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 页面标题 */}
          <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h1 className="text-2xl font-bold text-gray-900">用户管理</h1>
            <p className="text-gray-600 mt-1">管理系统用户账户和权限</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* 工具栏 */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="搜索用户名..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-4 pr-12 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      className="absolute right-2 top-1.5 p-1.5 text-gray-400 hover:text-indigo-600 transition-colors duration-200"
                    >
                      <FaSearch />
                    </button>
                  </div>
                </div>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors duration-200 flex items-center"
                >
                  <FaPlus className="mr-2" />
                  创建用户
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
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value={10}>10 条</option>
                  <option value={15}>15 条</option>
                  <option value={20}>20 条</option>
                </select>
              </div>
            </div>

            {/* 用户表格 */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedUsers.map((user, index) => (
                    <tr
                      key={user.id}
                      className="hover:bg-gray-50 transition-all duration-300 hover:shadow-md"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 ${getAvatarColor(user.role)} rounded-full flex items-center justify-center transform transition-transform duration-300 hover:scale-110`}>
                            <FaBullseye className={`text-sm ${getAvatarTextColor(user.role)}`} />
                          </div>
                          <span className="text-sm font-medium text-gray-900 hover:text-indigo-600 transition-colors duration-200">{user.username}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getRoleBadge(user.role)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.createdAt}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => openEditModal(user)}
                          className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 px-2 py-1 rounded mr-2 transition-all duration-200"
                        >
                          <FaEdit className="inline mr-1" /> 编辑
                        </button>
                        <button
                          onClick={() => openDeleteModal(user)}
                          className="text-red-600 hover:text-red-900 hover:bg-red-50 px-2 py-1 rounded transition-all duration-200"
                        >
                          <FaTrash className="inline mr-1" /> 删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* 分页 */}
            <div className="px-6 py-4 border-t border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-500">
                  显示 {(currentPage - 1) * pageSize + 1} 到 {Math.min(currentPage * pageSize, filteredUsers.length)} 条，共 {filteredUsers.length} 条记录
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 text-gray-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:disabled:bg-transparent"
                  >
                    <FaTimes className="text-xs rotate-180" />
                  </button>
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    const page = i + 1
                    return (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`px-3 py-1 rounded transition-all duration-200 ${
                          currentPage === page
                            ? 'bg-indigo-600 text-white'
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
                    <FaTimes className="text-xs" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />

      {/* 创建用户模态框 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl max-w-md w-full mx-4 shadow-xl">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">创建新用户</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
                >
                  <FaTimes />
                </button>
              </div>
            </div>

            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="3-20个字符，只能包含字母、数字和下划线"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">用户名只能包含字母、数字和下划线</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  密码 <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="请输入8-20位密码，不能包含空格"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">8-20个字符，不能包含空格</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  确认密码 <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={newUser.confirmPassword}
                  onChange={(e) => setNewUser({ ...newUser, confirmPassword: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="请再次输入密码"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户角色 <span className="text-red-500">*</span>
                </label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value as 'admin' | 'user' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                >
                  <option value="user">用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700 transition-colors duration-200"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
                >
                  创建用户
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 编辑用户模态框 */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl max-w-md w-full mx-4 shadow-xl">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">编辑用户</h3>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
                >
                  <FaTimes />
                </button>
              </div>
            </div>

            <form onSubmit={handleEditUser} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名
                </label>
                <input
                  type="text"
                  value={editUser.username}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600 cursor-not-allowed"
                  placeholder="用户名不可修改"
                />
                <p className="text-xs text-gray-500 mt-1">用户名不可修改</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户角色 <span className="text-red-500">*</span>
                </label>
                <select
                  value={editUser.role}
                  onChange={(e) => setEditUser({ ...editUser, role: e.target.value as 'admin' | 'user' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                >
                  <option value="user">用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <p className="text-sm font-medium text-gray-700 mb-3">密码修改</p>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      新密码 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="password"
                      onChange={(e) => setEditUser({ ...editUser, password: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="请输入8-20位密码，不能包含空格"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">8-20个字符，不能包含空格</p>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      确认新密码 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="password"
                      onChange={(e) => setEditUser({ ...editUser, confirmPassword: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="请再次输入新密码"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700 transition-colors duration-200"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
                >
                  保存修改
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 删除确认模态框 */}
      <ConfirmModal
        isOpen={showDeleteModal}
        title="删除用户"
        message={`确定要删除用户 "${selectedUser?.username}" 吗？此操作不可撤销。`}
        confirmText="删除"
        cancelText="取消"
        type="danger"
        onConfirm={handleDeleteUser}
        onCancel={() => {
          setShowDeleteModal(false)
          setSelectedUser(null)
        }}
      />
  </div>
  )
}