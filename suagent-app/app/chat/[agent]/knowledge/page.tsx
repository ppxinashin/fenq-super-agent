'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { FaFilePdf, FaFileWord, FaFileExcel, FaFilePowerpoint, FaFileAlt, FaFileImage, FaFileCode, FaPlus, FaTrash, FaEye, FaCloudUploadAlt, FaSearch, FaChevronLeft, FaChevronRight } from 'react-icons/fa'
import ConfirmModal from '@/components/ConfirmModal'
import { toast } from 'react-hot-toast'
import { FilesAPI, FileInfo } from '@/api'
import { useAuth } from '@/contexts/AuthContext'

const getFileIcon = (contentType: string | undefined) => {
  if (!contentType) {
    return <FaFileAlt className="text-gray-500 text-2xl" />
  }
  
  const type = contentType.toLowerCase()
  if (type.includes('pdf')) {
    return <FaFilePdf className="text-red-500 text-2xl" />
  } else if (type.includes('word') || type.includes('document')) {
    return <FaFileWord className="text-blue-500 text-2xl" />
  } else if (type.includes('excel') || type.includes('spreadsheet')) {
    return <FaFileExcel className="text-green-500 text-2xl" />
  } else if (type.includes('powerpoint') || type.includes('presentation')) {
    return <FaFilePowerpoint className="text-orange-500 text-2xl" />
  } else if (type.includes('image')) {
    return <FaFileImage className="text-purple-500 text-2xl" />
  } else if (type.includes('text') || type.includes('code')) {
    return <FaFileCode className="text-gray-500 text-2xl" />
  }
  return <FaFileAlt className="text-gray-500 text-2xl" />
}

const getStatusBadge = (status: string | undefined) => {
  if (!status) {
    return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">未知</span>
  }
  
  switch (status) {
    case '已处理':
      return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">已处理</span>
    case '处理中':
      return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">处理中</span>
    case '失败':
      return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">失败</span>
    default:
      return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">{status}</span>
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number | undefined): string => {
  if (!bytes || bytes === 0) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

// 提取文件名（不含后缀）
const getFileNameWithoutExt = (filename: string | undefined): string => {
  if (!filename) return '未知文件'
  const lastDotIndex = filename.lastIndexOf('.')
  return lastDotIndex > 0 ? filename.substring(0, lastDotIndex) : filename
}

// 提取文件扩展名
const getFileExtension = (filename: string | undefined): string => {
  if (!filename) return 'UNKNOWN'
  const lastDotIndex = filename.lastIndexOf('.')
  return lastDotIndex > 0 ? filename.substring(lastDotIndex + 1).toUpperCase() : 'UNKNOWN'
}

export default function KnowledgePage() {
  const params = useParams()
  const { user } = useAuth()
  const agentId = params.agent as string
  const username = user?.username || 'unknown'

  const [files, setFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadFileName, setUploadFileName] = useState('')
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null)
  const [showChunks, setShowChunks] = useState(false)
  const [expandedChunks, setExpandedChunks] = useState<number[]>([])
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteModalType, setDeleteModalType] = useState<'single' | 'batch'>('single')
  const [fileToDelete, setFileToDelete] = useState<string | null>(null)
  const [fileChunks, setFileChunks] = useState<any[]>([])
  
  // 分页和搜索
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [total, setTotal] = useState(0)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [searchInput, setSearchInput] = useState('')

  // 加载文件列表
  const loadFiles = async (page: number = currentPage, keyword: string = searchKeyword) => {
    try {
      setLoading(true)
      const params: any = {
        agent_id: agentId,
        page,
        page_size: pageSize
      }
      
      if (keyword) {
        params.keyword = keyword
      }
      
      const response = await FilesAPI.getFileList(params)

      console.log('文件列表API响应:', response)

      if (response.code === 200) {
        // 根据API文档，数据在 response.data 中
        const fileData = response.data || response.result
        const fileList = fileData?.data || fileData?.files || []
        const totalCount = fileData?.total || 0
        
        console.log('解析的文件列表:', fileList)
        console.log('总数:', totalCount)
        
        setFiles(fileList)
        setTotal(totalCount)
        setCurrentPage(fileData?.page || page)
      } else {
        console.error('加载文件列表失败:', response)
        toast.error(response.message || '加载文件列表失败')
      }
    } catch (error: any) {
      console.error('加载文件列表错误:', error)
      toast.error(error.response?.data?.message || '加载文件列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (agentId) {
      loadFiles(1, '')
    }
  }, [agentId])

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedFiles(files.map(file => file.file_name))
    } else {
      setSelectedFiles([])
    }
  }

  const handleSelectFile = (fileName: string, checked: boolean) => {
    if (checked) {
      setSelectedFiles(prev => [...prev, fileName])
    } else {
      setSelectedFiles(prev => prev.filter(f => f !== fileName))
    }
  }

  const handleUploadFiles = () => {
    if (isUploading) {
      toast.error('正在上传中，请稍后...')
      return
    }

    const fileInput = document.createElement('input')
    fileInput.type = 'file'
    fileInput.multiple = false
    fileInput.accept = '.pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.xls'
    fileInput.onchange = async (e) => {
      const target = e.target as HTMLInputElement
      const fileList = target.files
      if (fileList && fileList.length > 0 && !isUploading) {
        const file = fileList[0]
        setUploadFileName(file.name)
        setShowUploadModal(true)
        setIsUploading(true)
        
        try {
          // 模拟上传进度
          const progressInterval = setInterval(() => {
            setUploadProgress(prev => {
              if (prev >= 90) {
                clearInterval(progressInterval)
                return 90
              }
              return prev + 10
            })
          }, 200)

          const response = await FilesAPI.uploadFile(agentId, file)
          
          clearInterval(progressInterval)
          setUploadProgress(100)

          if (response.code === 200) {
            // 立即重新加载文件列表
            await loadFiles(currentPage, searchKeyword)
            
            toast.success('文件上传成功！')
            
            // 短暂延迟后关闭模态框（让用户看到100%）
            setTimeout(() => {
              setShowUploadModal(false)
              setUploadProgress(0)
              setIsUploading(false)
              setUploadFileName('')
            }, 300)
          } else {
            throw new Error(response.message || '上传失败')
          }
        } catch (error: any) {
          console.error('上传文件错误:', error)
          setShowUploadModal(false)
          setUploadProgress(0)
          setIsUploading(false)
          toast.error(error.message || '文件上传失败')
          setUploadFileName('')
        }
      }
      fileInput.value = ''
    }
    fileInput.click()
  }

  const handleBatchDelete = () => {
    if (selectedFiles.length === 0) {
      toast.error('请选择要删除的文件')
      return
    }

    setDeleteModalType('batch')
    setShowDeleteModal(true)
  }

  const handleDeleteFile = (fileName: string) => {
    setDeleteModalType('single')
    setFileToDelete(fileName)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    try {
      if (deleteModalType === 'batch') {
        // 批量删除
        const response = await FilesAPI.batchDeleteFiles({
          agent_id: agentId,
          sources: selectedFiles
        })

        if (response.code === 200) {
          toast.success('文件删除成功！')
          setSelectedFiles([])
          await loadFiles(currentPage, searchKeyword)
        } else {
          toast.error(response.message || '批量删除失败')
        }
      } else if (deleteModalType === 'single' && fileToDelete !== null) {
        // 单个删除
        const response = await FilesAPI.deleteFile({
          agent_id: agentId,
          source: fileToDelete
        })

        if (response.code === 200) {
          toast.success('文件删除成功！')
          await loadFiles(currentPage, searchKeyword)
        } else {
          toast.error(response.message || '删除失败')
        }
        setFileToDelete(null)
      }
    } catch (error: any) {
      console.error('删除文件错误:', error)
      toast.error(error.response?.data?.message || '删除失败')
    } finally {
      setShowDeleteModal(false)
    }
  }

  const cancelDelete = () => {
    setShowDeleteModal(false)
    setFileToDelete(null)
  }

  const handleViewDetail = async (file: FileInfo) => {
    setSelectedFile(file)
    setShowDetailModal(true)
    setExpandedChunks([])
    setShowChunks(false)
    
    // 加载文件分片信息（使用文件名）
    try {
      const response = await FilesAPI.getFileChunks({
        agent_id: agentId,
        source: file.file_name
      })

      if (response.code === 200 && response.result) {
        setFileChunks(response.result.chunks || [])
      }
    } catch (error) {
      console.error('加载分片信息失败:', error)
    }
  }

  const toggleChunkExpand = (chunkIndex: number) => {
    setExpandedChunks(prev =>
      prev.includes(chunkIndex)
        ? prev.filter(i => i !== chunkIndex)
        : [...prev, chunkIndex]
    )
  }

  const handleSearch = () => {
    setSearchKeyword(searchInput)
    setCurrentPage(1)
    loadFiles(1, searchInput)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    loadFiles(page, searchKeyword)
  }

  const totalPages = Math.ceil(total / pageSize)

  if (loading && currentPage === 1) {
    return (
      <div className="bg-white font-inter h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载文件列表中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white font-inter h-full flex flex-col">
      {/* 知识库标题栏 */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">知识库</h2>
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-500">
              共 <span className="font-medium text-indigo-600">{total}</span> 个文档
            </div>
          </div>
        </div>
      </div>

      {/* 工具栏 */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          {/* 左侧：全选 */}
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
          </div>

          {/* 右侧：搜索框、上传、批量删除 */}
          <div className="flex items-center space-x-3">
            {/* 搜索框 */}
            <div className="flex items-stretch shadow-sm rounded-lg overflow-hidden">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="搜索文件名..."
                className="pl-4 pr-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:shadow-lg transition-all duration-200 w-64 h-[38px] border-0"
              />
              <button
                onClick={handleSearch}
                className="px-4 bg-white text-gray-600 hover:text-indigo-600 hover:bg-gray-50 transition-all duration-200 h-[38px] flex items-center justify-center border-l border-gray-200"
              >
                <FaSearch />
              </button>
            </div>

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
        </div>
      </div>

      {/* 文件列表表格 */}
      <div className="flex-1 overflow-y-auto">
        {files.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-gray-500">
            <FaFileAlt className="text-6xl mb-4 text-gray-300" />
            <p>{searchKeyword ? '没有找到匹配的文件' : '暂无文档，请上传文件'}</p>
          </div>
        ) : (
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
                <tr key={`${file.source}-${index}`} className="hover:bg-gray-50 transition-colors duration-200">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={file.file_name ? selectedFiles.includes(file.file_name) : false}
                      onChange={(e) => file.file_name && handleSelectFile(file.file_name, e.target.checked)}
                      className="text-indigo-600"
                      disabled={!file.file_name}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded flex items-center justify-center">
                        {getFileIcon(file.content_type)}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{getFileNameWithoutExt(file.file_name)}</p>
                        <p className="text-sm text-gray-500">{file.source || '未知路径'}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {getFileExtension(file.file_name)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatFileSize(file.file_size || 0)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(file.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {file.created_at ? new Date(file.created_at).toLocaleString('zh-CN') : '未知'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleViewDetail(file)}
                        className="text-indigo-600 hover:text-indigo-900 transition-colors p-1"
                        title="查看详情"
                      >
                        <FaEye />
                      </button>
                      <button
                        onClick={() => file.file_name && handleDeleteFile(file.file_name)}
                        className="text-red-500 hover:text-red-700 transition-colors p-1"
                        title="删除文件"
                        disabled={!file.file_name}
                      >
                        <FaTrash />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* 分页 */}
      {totalPages > 0 && (
        <div className="px-6 py-4 border-t border-gray-200 bg-white">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              显示 {(currentPage - 1) * pageSize + 1} 到 {Math.min(currentPage * pageSize, total)} 条，共 {total} 条记录
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1 || loading}
                className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 text-gray-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:disabled:bg-transparent"
              >
                <FaChevronLeft className="text-xs" />
              </button>
              
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                let page;
                if (totalPages <= 5) {
                  page = i + 1
                } else if (currentPage <= 3) {
                  page = i + 1
                } else if (currentPage >= totalPages - 2) {
                  page = totalPages - 4 + i
                } else {
                  page = currentPage - 2 + i
                }
                
                return (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    disabled={loading}
                    className={`px-3 py-1 rounded transition-all duration-200 ${
                      currentPage === page
                        ? 'bg-indigo-600 text-white'
                        : 'border border-gray-300 hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    {page}
                  </button>
                )
              })}
              
              {totalPages > 5 && <span className="text-gray-500">...</span>}
              
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages || loading}
                className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 text-gray-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:disabled:bg-transparent"
              >
                <FaChevronRight className="text-xs" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 上传模态框 */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">正在上传</h3>
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
                  <p className="font-medium">{selectedFile.file_name || '未知'}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">文件格式</span>
                  <p className="font-medium">{selectedFile.content_type || '未知'}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">文件大小</span>
                  <p className="font-medium">{formatFileSize(selectedFile.file_size || 0)}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">上传时间</span>
                  <p className="font-medium">{selectedFile.created_at ? new Date(selectedFile.created_at).toLocaleString('zh-CN') : '未知'}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">状态</span>
                  <p className="font-medium">{selectedFile.status || '未知'}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <span className="text-sm text-gray-500">分片数量</span>
                  <p className="font-medium">{fileChunks.length || selectedFile.total_chunks || 0}</p>
                </div>
              </div>

              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-md font-medium text-gray-900">分片信息 ({fileChunks.length})</h4>
                  <button
                    onClick={() => setShowChunks(!showChunks)}
                    className="text-sm text-indigo-600 hover:text-indigo-800"
                  >
                    {showChunks ? '收起' : '展开'}
                  </button>
                </div>
                {showChunks && (
                  <div className="space-y-2">
                    {fileChunks.length > 0 ? (
                      fileChunks.map((chunk) => (
                        <div key={chunk.chunk_index} className="border border-gray-200 rounded-lg overflow-hidden">
                          <div
                            className="flex items-center justify-between p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                            onClick={() => toggleChunkExpand(chunk.chunk_index)}
                          >
                            <div className="flex items-center space-x-3">
                              <span className="text-sm font-medium">分片 {chunk.chunk_index + 1}</span>
                              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                                已完成
                              </span>
                            </div>
                            <button className="text-gray-400 hover:text-gray-600">
                              {expandedChunks.includes(chunk.chunk_index) ? '收起' : '展开'}
                            </button>
                          </div>
                          {expandedChunks.includes(chunk.chunk_index) && (
                            <div className="p-4 bg-white border-t border-gray-200">
                              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                                {chunk.content}
                              </p>
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4 text-gray-500">
                        暂无分片信息
                      </div>
                    )}
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
