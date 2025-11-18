'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { UserInfo } from '../api'

interface AuthContextType {
  user: UserInfo | null
  login: (token: string, userInfo: UserInfo) => void
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // 页面加载时检查sessionStorage中的用户信息
  useEffect(() => {
    const token = sessionStorage.getItem('access_token')
    const userInfo = sessionStorage.getItem('user_info')

    if (token && userInfo) {
      try {
        const parsedUser = JSON.parse(userInfo)
        setUser(parsedUser)
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Failed to parse user info:', error)
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('user_info')
      }
    }
  }, [])

  const login = (token: string, userInfo: UserInfo) => {
    sessionStorage.setItem('access_token', token)
    sessionStorage.setItem('user_info', JSON.stringify(userInfo))
    setUser(userInfo)
    setIsAuthenticated(true)
  }

  const logout = () => {
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('user_info')
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}