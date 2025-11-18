import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from 'react-hot-toast'
import MobileRedirectProvider from '@/components/MobileRedirectProvider'

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "fen青超级智能体",
  description: "探索无限可能的AI世界，创建属于你的智能助手",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body
        className={`${inter.variable} font-sans antialiased`}
      >
        <MobileRedirectProvider>
          {children}
        </MobileRedirectProvider>
        <Toaster
          position="bottom-center"
          gutter={16}
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
              marginBottom: '20px',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#4ade80',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  );
}
