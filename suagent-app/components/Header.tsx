'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { FaRobot, FaPlus, FaUser, FaKey, FaBrain, FaSignOutAlt, FaBars, FaTimes, FaSync } from 'react-icons/fa'
import ConfirmModal from './ConfirmModal'
import { toast } from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'
import { getAvatarText, generateAvatarGradient } from '../utils/avatarHelper'
import { AuthAPI, UsersAPI } from '../api'

export default function Header() {
  const { user, logout, isAuthenticated } = useAuth()
  const username = user?.username || 'User'
  const userRole = user?.role || 'user'
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showMobileMenu, setShowMobileMenu] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [showLogoutModal, setShowLogoutModal] = useState(false)
  const [longTermMemory, setLongTermMemory] = useState(false)

  // 密码表单状态
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const router = useRouter()
  const pathname = usePathname()

  // 加载长期记忆设置
  useEffect(() => {
    const loadMemorySetting = async () => {
      try {
        const response = await UsersAPI.getMemorySetting()
        if (response.code === 200) {
          setLongTermMemory(response.result)
        }
      } catch (error) {
        console.error('加载记忆设置失败:', error)
      }
    }

    // 只有在用户已登录时才加载设置
    if (isAuthenticated) {
      loadMemorySetting()
    }
  }, [isAuthenticated])

  const tabs = [
    { name: '智能体市场', href: '/market', alwaysShow: true },
    { name: '智能体管理', href: '/agents', alwaysShow: true },
    { name: '用户管理', href: '/users', alwaysShow: false, adminOnly: true }
  ]

  const filteredTabs = tabs.filter(tab => {
    if (tab.adminOnly && userRole !== 'admin') return false
    return true
  })

  const handleLogout = () => {
    setShowLogoutModal(true)
  }

  const confirmLogout = async () => {
    try {
      // 调用登出API
      const logoutResponse = await AuthAPI.logout()

      // 检查API响应
      if (logoutResponse.code === 200) {
        console.log('服务器登出成功:', logoutResponse.message)
      } else {
        console.warn('服务器登出响应异常:', logoutResponse.message)
      }
    } catch (error) {
      console.error('Logout API error:', error)
      // 即使API调用失败，也继续本地登出
    }

    // 本地登出 - 清除sessionStorage和AuthContext状态
    logout()
    toast.success('退出登录成功')
    setShowUserMenu(false)
    setShowLogoutModal(false)
    router.push('/login')
  }

  const cancelLogout = () => {
    setShowLogoutModal(false)
  }

  const handlePasswordInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()

    // 验证所有字段都已填写
    if (!passwordData.currentPassword.trim()) {
      toast.error('请输入当前密码！')
      return
    }

    if (!passwordData.newPassword.trim()) {
      toast.error('请输入新密码！')
      return
    }

    if (!passwordData.confirmPassword.trim()) {
      toast.error('请确认新密码！')
      return
    }

    // 验证新密码
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('新密码和确认密码不一致！')
      return
    }

    if (passwordData.newPassword.length < 8 || passwordData.newPassword.length > 20) {
      toast.error('新密码长度必须为8-20位！')
      return
    }

    if (/\s/.test(passwordData.newPassword)) {
      toast.error('新密码不能包含空格！')
      return
    }

    // 调用修改密码 API
    try {
      const changePasswordResponse = await AuthAPI.changePassword({
        old_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
        confirm_password: passwordData.confirmPassword
      })

      if (changePasswordResponse.code === 200) {
        toast.success('密码修改成功！')
        setShowPasswordModal(false)
        setShowUserMenu(false)
        setPasswordData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        })
      } else {
        toast.error(changePasswordResponse.message || '密码修改失败！')
      }
    } catch (error: any) {
      console.error('修改密码错误:', error)
      const errorMessage = error.response?.data?.message || error.message || '密码修改失败！'
      toast.error(errorMessage)
    }
  }

  const handleMemoryToggle = async () => {
    try {
      const newSetting = !longTermMemory
      const response = await UsersAPI.setMemorySetting({ enabled: newSetting })

      if (response.code === 200) {
        setLongTermMemory(newSetting)
        toast.success(newSetting ? '长期记忆已开启' : '长期记忆已关闭')
      } else {
        toast.error(response.message || '设置记忆状态失败')
      }
    } catch (error: any) {
      console.error('设置记忆状态错误:', error)
      const errorMessage = error.response?.data?.message || error.message || '设置记忆状态失败'
      toast.error(errorMessage)
    }
  }

  const handleSyncMemory = async () => {
    try {
      const response = await UsersAPI.syncMemory()
      if (response.code === 200) {
        toast.success('记忆同步完成！')
      } else if (response.code === 299) {
        toast.warning('请先开启长期记忆功能')
      } else {
        toast.error(response.message || '记忆同步失败')
      }
    } catch (error: any) {
      console.error('记忆同步错误:', error)
      const errorMessage = error.response?.data?.message || error.message || '记忆同步失败'
      toast.error(errorMessage)
    }
    setShowUserMenu(false)
  }

  // 判断是否应该隐藏新建按钮的页面，只在市场页面显示
  const shouldHideCreateButton = pathname !== '/market'


  return (
    <>
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo 和移动端菜单按钮 */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                className="lg:hidden text-gray-600 hover:text-gray-900 focus:outline-none"
              >
                {showMobileMenu ? <FaTimes /> : <FaBars />}
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <FaRobot className="text-white text-lg" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">fen青超级智能体</h1>
                  <p className="text-xs text-gray-500">FENQ Super Agents</p>
                </div>
              </div>
            </div>

            {/* 桌面端标签导航 */}
            <nav className="hidden lg:flex items-center space-x-1">
              {filteredTabs.map((tab) => (
                <button
                  key={tab.href}
                  onClick={() => router.push(tab.href)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                    pathname === tab.href
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>

  
            {/* 右侧按钮 */}
            <div className="flex items-center space-x-4">
              {/* 新建按钮 - 桌面端显示，但在管理和用户页面隐藏 */}
              {!shouldHideCreateButton && (
                <button
                  onClick={() => router.push('/agents/create')}
                  className="hidden md:flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 transform hover:-translate-y-0.5"
                >
                  <FaPlus />
                  <span>新建</span>
                </button>
              )}

              {/* 用户头像和菜单 */}
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="w-10 h-10 rounded-full flex items-center justify-center hover:ring-2 hover:ring-indigo-500 transition-all duration-200 text-white font-bold text-sm border-2 border-white shadow-lg"
                  style={{
                    background: generateAvatarGradient(username),
                    textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                  }}
                >
                  {getAvatarText(username)}
                </button>

                {/* 用户下拉菜单 */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                    <div className="px-4 py-2 border-b border-gray-200">
                      <p className="text-sm font-medium text-gray-900">{username}</p>
                      <p className="text-xs text-gray-500 capitalize">{userRole === 'admin' ? '管理员' : '用户'}</p>
                    </div>
                    <button
                      onClick={() => {
                        setShowPasswordModal(true)
                        setShowUserMenu(false)
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center transition-colors"
                    >
                      <FaKey className="mr-3 text-gray-400" />
                      修改密码
                    </button>
                    <div className="px-4 py-2 border-t border-gray-200 flex items-center justify-between">
                      <div className="flex items-center flex-1">
                        <FaBrain className="mr-3 text-gray-400" />
                        <span className="text-sm text-gray-700">开启长期记忆</span>
                      </div>
                      <button
                        type="button"
                        onClick={handleMemoryToggle}
                        className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                          longTermMemory ? 'bg-indigo-600' : 'bg-gray-200'
                        }`}
                        role="switch"
                        aria-checked={longTermMemory}
                      >
                        <span
                          className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                            longTermMemory ? 'translate-x-5' : 'translate-x-0'
                          }`}
                        />
                      </button>
                    </div>
                    {longTermMemory && (
                      <button
                        onClick={handleSyncMemory}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center transition-colors"
                      >
                        <FaSync className="mr-3 text-gray-400" />
                        同步记忆
                      </button>
                    )}
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center border-t border-gray-200 transition-colors"
                    >
                      <FaSignOutAlt className="mr-3" />
                      退出登录
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 移动端菜单 */}
          {showMobileMenu && (
            <div className="lg:hidden border-t border-gray-200 py-4">
              <nav className="flex flex-col space-y-2">
                {/* 移动端只显示智能体市场 */}
                <button
                  onClick={() => {
                    router.push('/market')
                    setShowMobileMenu(false)
                  }}
                  className={`px-4 py-2 text-left text-sm font-medium rounded-lg transition-all duration-200 ${
                    pathname === '/market'
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  智能体市场
                </button>
              </nav>
              {/* 移动端新建按钮 - 但在管理和用户页面隐藏 */}
              {!shouldHideCreateButton && (
                <div className="mt-4">
                  <button
                    onClick={() => {
                      router.push('/agents/create')
                      setShowMobileMenu(false)
                    }}
                    className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200"
                  >
                    <FaPlus />
                    <span>新建</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      {/* 修改密码模态框 */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 w-full transform transition-all">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">修改密码</h3>
              <button
                onClick={() => setShowPasswordModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <FaTimes />
              </button>
            </div>

            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  当前密码 <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  name="currentPassword"
                  value={passwordData.currentPassword}
                  onChange={handlePasswordInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="请输入当前密码"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  新密码 <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  name="newPassword"
                  value={passwordData.newPassword}
                  onChange={handlePasswordInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="请输入新密码（8-20位，不含空格）"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  确认新密码 <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={passwordData.confirmPassword}
                  onChange={handlePasswordInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="请再次输入新密码"
                />
              </div>

              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-xs text-gray-600">
                  <span className="font-medium">密码要求：</span>
                  8-20个字符，不允许包含空格
                </p>
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordModal(false)
                    setPasswordData({
                      currentPassword: '',
                      newPassword: '',
                      confirmPassword: ''
                    })
                  }}
                  className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  确认修改
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 点击外部关闭菜单 */}
      {showUserMenu && (
        <div
          className="fixed inset-0"
          style={{ zIndex: 30 }}
          onClick={() => setShowUserMenu(false)}
        />
      )}

      {/* 退出登录确认模态框 */}
      <ConfirmModal
        isOpen={showLogoutModal}
        title="退出登录"
        message="确定要退出登录吗？"
        confirmText="退出"
        cancelText="取消"
        type="warning"
        onConfirm={confirmLogout}
        onCancel={cancelLogout}
      />
    </>
  )
}