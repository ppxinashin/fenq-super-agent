'use client'

import { useState } from 'react'
import { FaFilePdf, FaFileWord, FaFileExcel, FaFilePowerpoint, FaFileAlt, FaPlus, FaTrash, FaDownload, FaEye, FaCloudUploadAlt } from 'react-icons/fa'
import ConfirmModal from '@/components/ConfirmModal'
import { toast } from 'react-hot-toast'

interface FileData {
  id: number
  name: string
  format: string
  size: string
  status: string
  time: string
  uuid?: string
  chunks: Array<{
    id: number
    size: string
    status: string
    content: string
  }>
}

const mockFiles: FileData[] = [
  {
    id: 1,
    name: 'Spring Boot实战指南',
    format: 'PDF',
    size: '2.4 MB',
    status: '解析完成',
    time: '2024-12-01 14:30',
    uuid: 'file-uuid-1',
    chunks: [
      { id: 1, size: '512 KB', status: '已完成', content: 'Spring Boot是一个快速开发框架，它基于Spring框架，提供了自动配置和快速启动的能力。本章将介绍Spring Boot的核心特性和基本用法。' },
      { id: 2, size: '512 KB', status: '已完成', content: 'Spring Boot的自动配置是其核心特性之一。通过智能的类路径检测，Spring Boot可以自动配置应用程序所需的大部分组件，大大简化了开发工作。' },
      { id: 3, size: '512 KB', status: '已完成', content: 'Spring Boot Actuator提供了生产级别的监控和管理功能。通过HTTP端点，开发者可以监控应用程序的健康状况、性能指标等信息。' },
      { id: 4, size: '896 KB', status: '已完成', content: 'Spring Boot的安全特性基于Spring Security框架，提供了完整的认证和授权功能。支持多种认证方式，包括基于表单的认证、OAuth2、JWT等。' }
    ]
  },
  {
    id: 2,
    name: '微服务架构设计模式',
    format: 'PDF',
    size: '3.1 MB',
    status: '解析完成',
    time: '2024-12-01 15:45',
    uuid: 'file-uuid-2',
    chunks: [
      { id: 1, size: '512 KB', status: '已完成', content: '微服务架构是一种将应用程序拆分为一组小型服务的方法。每个服务都运行在自己的进程中，通过轻量级的通信机制进行交互。这种架构模式提供了更好的可伸缩性和灵活性。' },
      { id: 2, size: '512 KB', status: '已完成', content: '服务发现是微服务架构中的关键组件。它允许服务自动注册和发现其他服务，而不需要硬编码网络位置。常见的服务发现工具包括Eureka、Consul和Zookeeper等。' },
      { id: 3, size: '512 KB', status: '已完成', content: 'API网关是微服务架构中的重要模式。它作为系统的统一入口，负责请求路由、负载均衡、认证授权等功能。常用的API网关包括Spring Cloud Gateway、Zuul等。' },
      { id: 4, size: '512 KB', status: '已完成', content: '分布式配置管理是微服务架构的必要组件。它允许在不重启服务的情况下动态更新配置。Spring Cloud Config、Apollo等都是优秀的配置管理解决方案。' },
      { id: 5, size: '512 KB', status: '已完成', content: '服务熔断和降级是微服务架构中的重要容错机制。当某个服务出现故障时，熔断器可以快速失败，避免级联故障。Hystrix、Resilience4j等都是常用的熔断器实现。' },
      { id: 6, size: '512 KB', status: '已完成', content: '分布式链路追踪是微服务架构中的调试利器。它可以帮助开发者理解请求在多个服务之间的流转过程。Zipkin、Jaeger等都是主流的链路追踪工具。' },
      { id: 7, size: '48 KB', status: '已完成', content: '容器化部署是微服务架构的最佳实践。Docker和Kubernetes等容器技术可以简化应用的部署和管理，提供更好的资源利用率和可移植性。' }
    ]
  },
  {
    id: 3,
    name: 'Java并发编程实战',
    format: 'PDF',
    size: '2.8 MB',
    status: '未解析',
    time: '2024-12-01 16:20',
    uuid: 'file-uuid-3',
    chunks: []
  }
]

const getFileIcon = (format: string) => {
  switch (format.toUpperCase()) {
    case 'PDF':
      return <FaFilePdf className="text-red-500" />
    case 'WORD':
    case 'DOC':
    case 'DOCX':
      return <FaFileWord className="text-blue-500" />
    case 'EXCEL':
    case 'XLS':
    case 'XLSX':
      return <FaFileExcel className="text-green-500" />
    case 'PPT':
    case 'PPTX':
      return <FaFilePowerpoint className="text-orange-500" />
    default:
      return <FaFileAlt className="text-gray-500" />
  }
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case '解析完成':
      return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">解析完成</span>
    case '未解析':
      return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">未解析</span>
    default:
      return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">未知</span>
  }
}

export default function KnowledgePage() {
  const [files, setFiles] = useState<FileData[]>(mockFiles)
  const [selectedFiles, setSelectedFiles] = useState<number[]>([])
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadFileName, setUploadFileName] = useState('')
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [isUploading, setIsUploading] = useState(false) // 防止重复上传
  const [selectedFile, setSelectedFile] = useState<FileData | null>(null)
  const [showChunks, setShowChunks] = useState(false)
  const [expandedChunks, setExpandedChunks] = useState<string[]>([])
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteModalType, setDeleteModalType] = useState<'single' | 'batch'>('single')
  const [fileToDelete, setFileToDelete] = useState<number | null>(null)

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedFiles(files.map(file => file.id))
    } else {
      setSelectedFiles([])
    }
  }

  const handleSelectFile = (fileId: number, checked: boolean) => {
    if (checked) {
      setSelectedFiles(prev => [...prev, fileId])
    } else {
      setSelectedFiles(prev => prev.filter(id => id !== fileId))
    }
  }

  const handleUploadFiles = () => {
    if (isUploading) {
      toast.error('正在上传中，请稍后...')
      return
    }

    const fileInput = document.createElement('input')
    fileInput.type = 'file'
    fileInput.multiple = true
    fileInput.onchange = (e) => {
      const target = e.target as HTMLInputElement
      const fileList = target.files
      if (fileList && fileList.length > 0 && !isUploading) {
        // 只取第一个文件
        const fileName = fileList[0].name
        setUploadFileName(fileName)
        setShowUploadModal(true)
        setIsUploading(true)
        simulateUpload(fileName)
      }
      // 清理input元素，避免重复触发
      fileInput.value = ''
    }
    fileInput.click()
  }

  const simulateUpload = (fileName: string) => {
    setUploadProgress(0)
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setTimeout(() => {
            setShowUploadModal(false)
            setUploadProgress(0)
            setIsUploading(false)
            toast.success('文件上传成功！')
            // 添加新文件到列表
            const maxId = Math.max(...files.map(f => f.id), 0)
            const newFile: FileData = {
              id: maxId + 1,
              name: fileName,
              format: fileName.split('.').pop()?.toUpperCase() || 'UNKNOWN',
              size: '1.5 MB',
              status: '解析完成',
              time: new Date().toLocaleString('zh-CN'),
              uuid: `file-uuid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              chunks: [
                { id: 1, size: '512 KB', status: '已完成', content: '这是第一个分片的内容，包含了文件的主要信息。' },
                { id: 2, size: '512 KB', status: '已完成', content: '这是第二个分片的内容，包含了文件的重要细节。' },
                { id: 3, size: '476 KB', status: '已完成', content: '这是第三个分片的内容，包含了文件的补充说明。' }
              ]
            }
            setFiles(prev => {
              const updated = [...prev, newFile]
              console.log('Files after upload:', updated)
              return updated
            })
            setUploadFileName('') // 清空上传文件名
          }, 500)
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  const handleBatchDelete = () => {
    if (selectedFiles.length === 0) {
      toast.error('请选择要删除的文件')
      return
    }

    // 显示批量删除确认
    setDeleteModalType('batch')
    setShowDeleteModal(true)
  }

  const handleDeleteFile = (fileId: number) => {
    setDeleteModalType('single')
    setFileToDelete(fileId)
    setShowDeleteModal(true)
  }

  const confirmDelete = () => {
    if (deleteModalType === 'batch') {
      // 批量删除
      setFiles(prev => prev.filter(file => !selectedFiles.includes(file.id)))
      setSelectedFiles([])
      toast.success('文件删除成功！')
    } else if (deleteModalType === 'single' && fileToDelete !== null) {
      // 单个删除
      setFiles(prev => prev.filter(file => file.id !== fileToDelete))
      toast.success('文件删除成功！')
      setFileToDelete(null)
    }
    setShowDeleteModal(false)
  }

  const cancelDelete = () => {
    setShowDeleteModal(false)
    setFileToDelete(null)
  }

  const handleViewDetail = (file: FileData) => {
    setSelectedFile(file)
    setShowDetailModal(true)
    setExpandedChunks([])
  }

  const toggleChunkExpand = (chunkId: number) => {
    const uniqueChunkId = selectedFile ? `${selectedFile.id}-${chunkId}` : chunkId.toString()
    setExpandedChunks(prev =>
      prev.includes(uniqueChunkId)
        ? prev.filter(id => id !== uniqueChunkId)
        : [...prev, uniqueChunkId]
    )
  }

  return (
    <div className="bg-white font-inter h-full">
      {/* 知识库标题栏 */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">知识库</h2>
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-500">
              共 <span className="font-medium text-indigo-600">{files.length}</span> 个文档
            </div>
          </div>
        </div>
      </div>

      {/* 工具栏 */}
      <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={selectedFiles.length === files.length && files.length > 0}
              onChange={(e) => handleSelectAll(e.target.checked)}
              className="mr-2 text-indigo-600"
            />
            <span className="text-sm text-gray-700">全选</span>
          </label>

          <button
            onClick={handleUploadFiles}
            disabled={isUploading}
            className={`px-4 py-2 rounded-md transition-colors flex items-center text-sm ${
              isUploading
                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }`}
          >
            <FaPlus className="mr-2" />
            {isUploading ? '上传中...' : '上传文档'}
          </button>

          <button
            onClick={handleBatchDelete}
            disabled={selectedFiles.length === 0}
            className={`px-4 py-2 rounded-md transition-colors flex items-center text-sm ${
              selectedFiles.length > 0
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <FaTrash className="mr-2" />
            批量删除 ({selectedFiles.length})
          </button>
        </div>

        <div className="relative">
          <input
            type="text"
            placeholder="搜索文件名..."
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <i className="fas fa-search absolute left-3 top-3 text-gray-400" />
        </div>
      </div>

      {/* 文件列表表格 */}
      <div className="overflow-y-auto" style={{ height: 'calc(100vh - 180px)' }}>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 sticky top-0">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <input
                  type="checkbox"
                  checked={selectedFiles.length === files.length && files.length > 0}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                  className="text-indigo-600"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                数据名称
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                文件格式
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                数据大小
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                上传时间
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {files.map((file, index) => (
              <tr key={file.uuid || `file-${file.id}-${index}`} className="hover:bg-gray-50 transition-colors duration-200">
                <td className="px-6 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    checked={selectedFiles.includes(file.id)}
                    onChange={(e) => handleSelectFile(file.id, e.target.checked)}
                    className="text-indigo-600"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded flex items-center justify-center">
                      {getFileIcon(file.format)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-500">demo/{file.name}.{file.format.toLowerCase()}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {file.format}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {file.size}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(file.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {file.time}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleViewDetail(file)}
                      className="text-indigo-600 hover:text-indigo-900 transition-colors p-1"
                    >
                      <FaEye />
                    </button>
                    <button
                      onClick={() => handleDeleteFile(file.id)}
                      className="text-red-500 hover:text-red-700 transition-colors p-1"
                    >
                      <FaTrash />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 上传模态框 */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">正在上传</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <span className="text-xl">×</span>
              </button>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FaCloudUploadAlt className="text-indigo-600 text-2xl" />
              </div>
              <p className="text-gray-700 mb-4">{uploadFileName}</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500">{uploadProgress}%</p>
            </div>
          </div>
        </div>
      )}

      {/* 详情模态框 */}
      {showDetailModal && selectedFile && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">文件详情</h3>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <span className="text-xl">×</span>
                </button>
              </div>
            </div>
            <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(80vh - 140px)' }}>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">文件名称</span>
                  <p className="font-medium">{selectedFile.name}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">文件格式</span>
                  <p className="font-medium">{selectedFile.format}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">文件大小</span>
                  <p className="font-medium">{selectedFile.size}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">上传时间</span>
                  <p className="font-medium">{selectedFile.time}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">状态</span>
                  <p className="font-medium">{selectedFile.status}</p>
                </div>
              </div>

              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-md font-medium text-gray-900">分片信息</h4>
                  <button
                    onClick={() => setShowChunks(!showChunks)}
                    className="text-sm text-indigo-600 hover:text-indigo-800"
                  >
                    {showChunks ? '收起' : '展开'}
                  </button>
                </div>
                {showChunks && (
                  <div className="space-y-2">
                    {selectedFile.chunks.map(chunk => (
                      <div key={`${selectedFile.id}-${chunk.id}`} className="border border-gray-200 rounded-lg overflow-hidden">
                        <div
                          className="flex items-center justify-between p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                          onClick={() => toggleChunkExpand(chunk.id)}
                        >
                          <div className="flex items-center space-x-3">
                            <span className="text-sm font-medium">分片 {chunk.id}</span>
                            <span className="text-sm text-gray-600">{chunk.size}</span>
                            <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                              {chunk.status}
                            </span>
                          </div>
                          <button className="text-gray-400 hover:text-gray-600">
                            {expandedChunks.includes(`${selectedFile.id}-${chunk.id}`) ? '收起' : '展开'}
                          </button>
                        </div>
                        {expandedChunks.includes(`${selectedFile.id}-${chunk.id}`) && (
                          <div className="p-4 bg-white border-t border-gray-200">
                            <p className="text-sm text-gray-700 leading-relaxed">
                              {chunk.content}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="p-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-2">
              <button
                onClick={() => setShowDetailModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                关闭
              </button>
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
                <FaDownload className="inline mr-2" />
                下载
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 删除确认模态框 */}
      <ConfirmModal
        isOpen={showDeleteModal}
        title={deleteModalType === 'batch' ? '批量删除文件' : '删除文件'}
        message={deleteModalType === 'batch'
          ? `确定要删除选中的 ${selectedFiles.length} 个文件吗？`
          : '确定要删除这个文件吗？'}
        confirmText="删除"
        cancelText="取消"
        type="danger"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  )
}