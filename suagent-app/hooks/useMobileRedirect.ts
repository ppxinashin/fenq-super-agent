'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

// 检测是否为移动端
export const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 1024
}

// 需要显示"请在桌面端使用"提示的页面
const desktopOnlyPages = ['/users', '/agents']

// 检查路径是否为需要重定向的聊天框架页面
const shouldRedirectChatFramework = (pathname: string): boolean => {
  // 检查是否匹配 /chat/[agent] 格式但不包含 [session]
  const chatFrameworkPattern = /^\/chat\/[^\/]+(\/[^\/]+)?$/
  const hasSession = pathname.split('/').length >= 4 // /chat/agent/session 格式有4段

  return chatFrameworkPattern.test(pathname) && !hasSession
}

// 检查路径是否为编辑页面
const isEditPage = (pathname: string): boolean => {
  return pathname.startsWith('/agents/edit/') || pathname.startsWith('/users/edit/')
}

export function useMobileRedirect() {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // 检测移动端
    const checkMobileAndRedirect = () => {
      if (isMobile()) {
        // 检查是否为桌面端专属页面或编辑页面
        if (desktopOnlyPages.includes(pathname) || isEditPage(pathname)) {
          // 对于管理页面和编辑页面，显示提示而不是重定向
          return
        }

        // 检查是否为聊天框架页面（需要重定向）
        if (shouldRedirectChatFramework(pathname)) {
          // 从 /chat/[agent] 提取 agentId 并创建新session，跳转到聊天会话页面
          const pathSegments = pathname.split('/')
          const agentId = pathSegments[2]
          if (agentId) {
            const sessionId = Date.now().toString()
            router.replace(`/chat/${agentId}/${sessionId}`)
            return
          }
        }

        // 检查是否为管理页面，需要重定向到市场
        if (pathname === '/agents' || pathname === '/users') {
          router.replace('/market')
        }
      }
    }

    checkMobileAndRedirect()

    // 监听窗口大小变化
    const handleResize = () => {
      checkMobileAndRedirect()
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [pathname, router])
}