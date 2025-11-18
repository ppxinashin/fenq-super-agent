import apiClient from './config';
import { ApiResponse } from './types';

/**
 * 处理 API 响应的通用工具函数
 */
export class APIUtils {
  /**
   * 检查响应是否成功
   */
  static isSuccess<T>(response: ApiResponse<T>): boolean {
    return response.code === 200;
  }

  /**
   * 获取错误信息
   */
  static getErrorMessage(error: any): string {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return '请求失败';
  }

  /**
   * 处理 API 错误
   */
  static handleError(error: any): never {
    const message = this.getErrorMessage(error);
    console.error('API Error:', error);
    throw new Error(message);
  }

  /**
   * 带重试机制的请求
   */
  static async withRetry<T>(
    requestFn: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<T> {
    let lastError: any;

    for (let i = 0; i < maxRetries; i++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error;
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
        }
      }
    }

    throw lastError;
  }

  /**
   * 超时处理包装器
   */
  static async withTimeout<T>(
    promise: Promise<T>,
    timeoutMs: number = 30000
  ): Promise<T> {
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('请求超时')), timeoutMs);
    });

    return Promise.race([promise, timeoutPromise]);
  }

  /**
   * 文件下载工具
   */
  static async downloadFile(url: string, filename: string): Promise<void> {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * 格式化文件大小
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * 生成随机字符串（用于文件名等）
   */
  static generateRandomString(length: number = 8): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  /**
   * 验证文件类型
   */
  static isValidFileType(file: File, allowedTypes: string[]): boolean {
    return allowedTypes.some(type => file.type.includes(type));
  }

  /**
   * 验证文件大小
   */
  static isValidFileSize(file: File, maxSizeMB: number = 10): boolean {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
  }
}

/**
 * 自定义错误类
 */
export class APIError extends Error {
  public code: number;
  public response?: any;

  constructor(message: string, code: number = 500, response?: any) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.response = response;
  }
}

/**
 * 流式响应处理工具
 */
export class StreamUtils {
  /**
   * 处理流式响应
   */
  static async processStream(
    response: Response,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      onError(new Error('无法读取流式响应'));
      return;
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          onComplete();
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    } catch (error) {
      onError(error as Error);
    } finally {
      reader.releaseLock();
    }
  }
}

export default APIUtils;