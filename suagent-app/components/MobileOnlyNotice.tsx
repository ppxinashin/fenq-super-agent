'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { FaDesktop, FaArrowLeft } from 'react-icons/fa'

export default function MobileOnlyNotice() {
  const router = useRouter()

  useEffect(() => {
    // 检测是否为移动端
    const checkMobile = () => {
      if (typeof window !== 'undefined') {
        return window.innerWidth < 1024
      }
      return false
    }

    // 如果不是移动端，重定向到首页
    if (!checkMobile()) {
      router.replace('/market')
    }
  }, [router])

  const handleBackToMarket = () => {
    router.push('/market')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 flex items-center justify-center p-4">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-bounce"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-bounce" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-md mx-auto">
        <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl p-8 text-center animate-fade-in">
          {/* 桌面图标 */}
          <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <FaDesktop className="text-white text-4xl" />
          </div>

          <h1 className="text-2xl font-bold text-white mb-4">
            请在桌面端使用
          </h1>

          <p className="text-white/80 mb-8 leading-relaxed">
            此功能仅支持桌面端浏览器访问，请在电脑上打开页面使用完整功能。
          </p>

          <button
            onClick={handleBackToMarket}
            className="w-full bg-white text-purple-600 py-3 px-6 rounded-xl font-semibold hover:bg-gray-100 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg flex items-center justify-center space-x-2"
          >
            <FaArrowLeft />
            <span>返回智能体市场</span>
          </button>
        </div>
      </div>

      </div>
  )
}