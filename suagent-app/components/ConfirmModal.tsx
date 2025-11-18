'use client'

import { FaExclamationTriangle, FaCheck, FaTimes } from 'react-icons/fa'

interface ConfirmModalProps {
  isOpen: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'warning' | 'danger' | 'info'
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  type = 'warning',
  onConfirm,
  onCancel
}: ConfirmModalProps) {
  if (!isOpen) return null

  const getIconAndColor = () => {
    switch (type) {
      case 'danger':
        return {
          icon: FaExclamationTriangle,
          bgColor: 'bg-red-100',
          iconColor: 'text-red-600',
          buttonBg: 'bg-red-600 hover:bg-red-700'
        }
      case 'info':
        return {
          icon: FaCheck,
          bgColor: 'bg-blue-100',
          iconColor: 'text-blue-600',
          buttonBg: 'bg-blue-600 hover:bg-blue-700'
        }
      default:
        return {
          icon: FaExclamationTriangle,
          bgColor: 'bg-yellow-100',
          iconColor: 'text-yellow-600',
          buttonBg: 'bg-yellow-600 hover:bg-yellow-700'
        }
    }
  }

  const { icon: Icon, bgColor, iconColor, buttonBg } = getIconAndColor()

  return (
    <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-md mx-4 w-full transform transition-all">
        <div className="text-center">
          {/* 图标 */}
          <div className={`w-16 h-16 ${bgColor} rounded-full flex items-center justify-center mx-auto mb-4`}>
            <Icon className={`text-2xl ${iconColor}`} />
          </div>

          {/* 标题 */}
          <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>

          {/* 消息 */}
          <p className="text-gray-600 mb-6">{message}</p>

          {/* 按钮 */}
          <div className="flex space-x-4">
            <button
              onClick={onCancel}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              {cancelText}
            </button>
            <button
              onClick={onConfirm}
              className={`flex-1 px-6 py-3 text-white rounded-lg transition-colors ${buttonBg}`}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}