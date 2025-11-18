import apiClient from './config';
import { ApiResponse, AgentHealthParams } from './types';

export class SystemAPI {
  /**
   * 根路径
   */
  static async root(): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.get<ApiResponse<Record<string, any>>>('/');
    return response.data;
  }

  /**
   * 健康检查
   */
  static async healthCheck(): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.get<ApiResponse<Record<string, any>>>('/health');
    return response.data;
  }

  /**
   * 智能体健康检测
   */
  static async agentHealth(params?: AgentHealthParams): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.get<ApiResponse<Record<string, any>>>('/agent_health', { params });
    return response.data;
  }
}

export default SystemAPI;