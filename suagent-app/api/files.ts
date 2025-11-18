import apiClient from './config';
import {
  ApiResponse,
  FileUploadResponse,
  FileListResponse,
  FileChunksResponse,
  FileDeleteResponse,
  FileBatchDeleteRequest,
  FileBatchDeleteResponse,
  FileListParams,
  FileChunkParams,
  FileDeleteParams,
} from './types';

export class FilesAPI {
  /**
   * 上传文件到知识库
   */
  static async uploadFile(agent_id: string, file: File): Promise<ApiResponse<FileUploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ApiResponse<FileUploadResponse>>(
      '/api/v1/files/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: { agent_id }
      }
    );
    return response.data;
  }

  /**
   * 查看知识库文件列表
   */
  static async getFileList(params: FileListParams): Promise<ApiResponse<FileListResponse>> {
    const response = await apiClient.get<ApiResponse<FileListResponse>>('/api/v1/files', { params });
    return response.data;
  }

  /**
   * 删除知识库文件
   */
  static async deleteFile(params: FileDeleteParams): Promise<ApiResponse<FileDeleteResponse>> {
    const response = await apiClient.delete<ApiResponse<FileDeleteResponse>>('/api/v1/files', { params });
    return response.data;
  }

  /**
   * 查看文件的分块详情
   */
  static async getFileChunks(params: FileChunkParams): Promise<ApiResponse<FileChunksResponse>> {
    const response = await apiClient.get<ApiResponse<FileChunksResponse>>('/api/v1/files/chunks', { params });
    return response.data;
  }

  /**
   * 批量删除知识库文件
   */
  static async batchDeleteFiles(data: FileBatchDeleteRequest): Promise<ApiResponse<FileBatchDeleteResponse>> {
    const response = await apiClient.post<ApiResponse<FileBatchDeleteResponse>>('/api/v1/files/batch-delete', data);
    return response.data;
  }
}

export default FilesAPI;