import apiClient from './config';
import {
  ApiResponse,
  Pageable,
  AgentCreateRequest,
  AgentCreateResponse,
  AgentUpdateRequest,
  AgentUpdateResponse,
  AgentToolsUpdateRequest,
  AgentMcpUpdateRequest,
  AgentDeleteResponse,
  AgentInfo,
  AgentSimpleInfo,
  AgentListItem,
  AgentListParams,
  AgentCardListParams,
} from './types';

export class AgentsAPI {
  /**
   * 创建智能体
   */
  static async createAgent(data: AgentCreateRequest): Promise<ApiResponse<AgentCreateResponse>> {
    const response = await apiClient.post<ApiResponse<AgentCreateResponse>>('/api/v1/agents', data);
    return response.data;
  }

  /**
   * 修改智能体
   */
  static async updateAgent(data: AgentUpdateRequest): Promise<ApiResponse<AgentUpdateResponse>> {
    const response = await apiClient.put<ApiResponse<AgentUpdateResponse>>('/api/v1/agents', data);
    return response.data;
  }

  /**
   * 智能体列表管理
   */
  static async getAgentManagementList(params?: AgentListParams): Promise<ApiResponse<Pageable<AgentListItem>>> {
    const response = await apiClient.get<ApiResponse<Pageable<AgentListItem>>>('/api/v1/agents', { params });
    return response.data;
  }

  /**
   * 智能体卡片展示
   */
  static async getAgentCardList(params?: AgentCardListParams): Promise<ApiResponse<Pageable<AgentSimpleInfo>>> {
    const response = await apiClient.get<ApiResponse<Pageable<AgentSimpleInfo>>>('/api/v1/agents/cards', { params });
    return response.data;
  }

  /**
   * 获取智能体详情
   */
  static async getAgentById(agent_id: string): Promise<ApiResponse<AgentInfo>> {
    const response = await apiClient.get<ApiResponse<AgentInfo>>(`/api/v1/agents/${agent_id}`);
    return response.data;
  }

  /**
   * 删除智能体
   */
  static async deleteAgent(agent_id: string): Promise<ApiResponse<AgentDeleteResponse>> {
    const response = await apiClient.delete<ApiResponse<AgentDeleteResponse>>(`/api/v1/agents/${agent_id}`);
    return response.data;
  }

  /**
   * 更新智能体工具
   */
  static async updateAgentTools(data: AgentToolsUpdateRequest): Promise<ApiResponse<AgentUpdateResponse>> {
    const response = await apiClient.put<ApiResponse<AgentUpdateResponse>>('/api/v1/agents/tools', data);
    return response.data;
  }

  /**
   * 更新智能体MCP配置
   */
  static async updateAgentMcp(data: AgentMcpUpdateRequest): Promise<ApiResponse<AgentUpdateResponse>> {
    const response = await apiClient.put<ApiResponse<AgentUpdateResponse>>('/api/v1/agents/mcp', data);
    return response.data;
  }
}

export default AgentsAPI;