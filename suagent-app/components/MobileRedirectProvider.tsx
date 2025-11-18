'use client'

import { useMobileRedirect } from '@/hooks/useMobileRedirect'

export default function MobileRedirectProvider({ children }: { children: React.ReactNode }) {
  useMobileRedirect()
  return <>{children}</>
}