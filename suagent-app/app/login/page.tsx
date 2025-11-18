'use client'

import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { FaUser, FaLock, FaEye, FaEyeSlash } from 'react-icons/fa'
import { useRouter } from 'next/navigation'
import { AuthAPI } from '../../api'
import { useAuth } from '../../contexts/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
  })
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!isLogin && formData.password !== formData.confirmPassword) {
      toast.error('密码和确认密码不一致！')
      return
    }

    if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      toast.error('用户名只能包含字母、数字和下划线！')
      return
    }

    if (formData.password.length < 8 || formData.password.length > 20) {
      toast.error('密码长度必须为8-20位！')
      return
    }

    if (/\s/.test(formData.password)) {
      toast.error('密码不能包含空格！')
      return
    }

    try {
      if (isLogin) {
        // 登录 API 调用
        const loginResponse = await AuthAPI.login({
          username: formData.username,
          password: formData.password
        });

        if (loginResponse.code === 200 && loginResponse.result) {
          // 使用AuthContext的login方法
          login(loginResponse.result.access_token, loginResponse.result.user_info);

          toast.success('登录成功！');
          setTimeout(() => {
            router.push('/market');
          }, 1000);
        } else {
          toast.error(loginResponse.message || '登录失败！');
        }
      } else {
        // 注册 API 调用
        const registerResponse = await AuthAPI.register({
          username: formData.username,
          password: formData.password,
          confirm_password: formData.confirmPassword
        });

        if (registerResponse.code === 200) {
          toast.success('注册成功！请登录');
          // 注册成功后切换到登录模式
          setIsLogin(true);
          // 清空密码字段
          setFormData(prev => ({
            ...prev,
            password: '',
            confirmPassword: ''
          }));
        } else {
          toast.error(registerResponse.message || '注册失败！');
        }
      }
    } catch (error: any) {
      console.error(isLogin ? '登录错误:' : '注册错误:', error);
      const errorMessage = error.response?.data?.message || error.message || (isLogin ? '登录失败！' : '注册失败！');
      toast.error(errorMessage);
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 font-['Inter'] relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-bounce"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-bounce" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-4xl mx-auto">
          {/* 桌面端完整布局 */}
          <div className="hidden lg:grid lg:grid-cols-2 gap-12 items-center">
            {/* 左侧内容 */}
            <div className="text-white animate-slide-up">
              <div className="mb-8">
                <h1 className="text-[clamp(2rem,5vw,3.5rem)] font-bold mb-4 leading-tight">
                  fen青<br />
                  <span className="text-yellow-300">超级智能体</span>
                </h1>
                <p className="text-xl text-white/80 mb-6 leading-relaxed">
                  探索无限可能的AI世界，创建属于你的智能助手
                </p>
                <div className="flex items-center space-x-6 text-sm text-white/70">
                  <div className="flex items-center">
                    <i className="fas fa-robot mr-2 text-blue-300"></i>
                    <span>智能对话</span>
                  </div>
                  <div className="flex items-center">
                    <i className="fas fa-cogs mr-2 text-green-300"></i>
                    <span>自定义工具</span>
                  </div>
                  <div className="flex items-center">
                    <i className="fas fa-brain mr-2 text-purple-300"></i>
                    <span>知识库管理</span>
                  </div>
                </div>
              </div>

              {/* 特色功能 */}
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-400 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <i className="fas fa-check text-white text-xs"></i>
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">个性化智能体</h3>
                    <p className="text-white/70 text-sm">根据需求创建专属的AI助手</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-green-400 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <i className="fas fa-check text-white text-xs"></i>
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">丰富的工具生态</h3>
                    <p className="text-white/70 text-sm">集成多种工具，扩展智能体能力</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-purple-400 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <i className="fas fa-check text-white text-xs"></i>
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">强大的知识库</h3>
                    <p className="text-white/70 text-sm">支持文档上传和智能检索</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 右侧表单 */}
            <div className="animate-fade-in">
              <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl p-8 hover:shadow-2xl transition-all duration-300">
                {/* 标签切换 */}
                <div className="flex mb-8">
                  <button
                    onClick={() => setIsLogin(true)}
                    className={`flex-1 py-3 px-4 text-center font-medium rounded-t-lg transition-all duration-300 ${
                      isLogin
                        ? 'bg-white text-purple-600 font-semibold'
                        : 'text-white/70 hover:text-white'
                    }`}
                  >
                    登录
                  </button>
                  <button
                    onClick={() => setIsLogin(false)}
                    className={`flex-1 py-3 px-4 text-center font-medium rounded-t-lg transition-all duration-300 ${
                      !isLogin
                        ? 'bg-white text-purple-600 font-semibold'
                        : 'text-white/70 hover:text-white'
                    }`}
                  >
                    注册
                  </button>
                </div>

                {/* 表单 */}
                <form onSubmit={handleSubmit}>
                  <h2 className="text-2xl font-bold text-white mb-6 text-center">
                    {isLogin ? '欢迎回来' : '创建账号'}
                  </h2>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">用户名</label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FaUser className="text-white/40" />
                        </div>
                        <input
                          type="text"
                          name="username"
                          value={formData.username}
                          onChange={handleInputChange}
                          className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                          placeholder="请输入用户名"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">密码</label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FaLock className="text-white/40" />
                        </div>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={formData.password}
                          onChange={handleInputChange}
                          className="w-full pl-10 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                          placeholder="请输入密码"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center text-white/40 hover:text-white transition-colors"
                        >
                          {showPassword ? <FaEyeSlash /> : <FaEye />}
                        </button>
                      </div>
                    </div>

                    {!isLogin && (
                      <div>
                        <label className="block text-white/80 text-sm font-medium mb-2">确认密码</label>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <FaLock className="text-white/40" />
                          </div>
                          <input
                            type={showConfirmPassword ? 'text' : 'password'}
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleInputChange}
                            className="w-full pl-10 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                            placeholder="请再次输入密码"
                            required
                          />
                          <button
                            type="button"
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            className="absolute inset-y-0 right-0 pr-3 flex items-center text-white/40 hover:text-white transition-colors"
                          >
                            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  <button
                    type="submit"
                    className="w-full mt-6 py-3 px-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
                  >
                    {isLogin ? '登录' : '注册'}
                  </button>

                  <div className="mt-6 text-center text-white/70 text-sm">
                    {isLogin ? '还没有账号？' : '已有账号？'}
                    <button
                      type="button"
                      onClick={() => setIsLogin(!isLogin)}
                      className="text-yellow-300 hover:text-yellow-200 font-medium ml-1"
                    >
                      {isLogin ? '立即注册' : '立即登录'}
                    </button>
                  </div>

                  {!isLogin && (
                    <div className="mt-4 text-center text-white/60 text-xs space-y-1">
                      <p>• 用户名：只能包含字母、数字和下划线</p>
                      <p>• 密码：8-20位字符，不允许空格</p>
                    </div>
                  )}
                </form>
              </div>
            </div>
          </div>

          {/* 移动端简化布局 */}
          <div className="lg:hidden">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-white mb-2">
                fen青超级智能体
              </h1>
            </div>

            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-6 animate-fade-in">
              {/* 标签切换 */}
              <div className="flex mb-6">
                <button
                  onClick={() => setIsLogin(true)}
                  className={`flex-1 py-2 px-4 text-center font-medium rounded-t-lg transition-all duration-300 ${
                    isLogin
                      ? 'bg-white text-purple-600 font-semibold'
                      : 'text-white/70 hover:text-white'
                  }`}
                >
                  登录
                </button>
                <button
                  onClick={() => setIsLogin(false)}
                  className={`flex-1 py-2 px-4 text-center font-medium rounded-t-lg transition-all duration-300 ${
                    !isLogin
                      ? 'bg-white text-purple-600 font-semibold'
                      : 'text-white/70 hover:text-white'
                  }`}
                >
                  注册
                </button>
              </div>

              {/* 表单 */}
              <form onSubmit={handleSubmit}>
                <div className="space-y-4">
                  <div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FaUser className="text-white/60" />
                      </div>
                      <input
                        type="text"
                        name="username"
                        value={formData.username}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                        placeholder="请输入用户名"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <FaLock className="text-white/60" />
                      </div>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                        placeholder="请输入密码"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-white/60 hover:text-white transition-colors"
                      >
                        {showPassword ? <FaEyeSlash /> : <FaEye />}
                      </button>
                    </div>
                  </div>

                  {!isLogin && (
                    <div>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FaLock className="text-white/60" />
                        </div>
                        <input
                          type={showConfirmPassword ? 'text' : 'password'}
                          name="confirmPassword"
                          value={formData.confirmPassword}
                          onChange={handleInputChange}
                          className="w-full pl-10 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                          placeholder="请再次输入密码"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center text-white/60 hover:text-white transition-colors"
                        >
                          {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  className="w-full py-3 px-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
                >
                  {isLogin ? '登录' : '注册'}
                </button>

                <div className="mt-4 text-center text-white/70 text-sm">
                  {isLogin ? '还没有账号？' : '已有账号？'}
                  <button
                    type="button"
                    onClick={() => setIsLogin(!isLogin)}
                    className="text-yellow-300 hover:text-yellow-200 font-medium ml-1"
                  >
                    {isLogin ? '立即注册' : '立即登录'}
                  </button>
                </div>

                {!isLogin && (
                  <div className="mt-4 text-center text-white/60 text-xs space-y-1">
                    <p>• 用户名：只能包含字母、数字和下划线</p>
                    <p>• 密码：8-20位字符，不允许空格</p>
                  </div>
                )}
              </form>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-in-out;
        }

        .animate-slide-up {
          animation: slide-up 0.6s ease-out;
        }

        .animate-bounce {
          animation: bounce 2s infinite;
        }
      `}</style>
    </div>
  )
}