'use client'

import { useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../contexts/AuthContext'

interface AuthProtectedProps {
  children: ReactNode
  fallback?: ReactNode
  redirectTo?: string
}

export default function AuthProtected({
  children,
  fallback = null,
  redirectTo = '/login'
}: AuthProtectedProps) {
  const { isAuthenticated } = useAuth()
  const router = useRouter()
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    // 给AuthContext一些时间来初始化认证状态
    const timer = setTimeout(() => {
      setIsChecking(false)
    }, 100)

    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    // 如果不在检查状态且未认证，重定向到登录页
    if (!isChecking && !isAuthenticated) {
      router.push(redirectTo)
    }
  }, [isChecking, isAuthenticated, router, redirectTo])

  // 如果正在检查或未认证，显示fallback或null
  if (isChecking || !isAuthenticated) {
    return <>{fallback}</>
  }

  return <>{children}</>
}