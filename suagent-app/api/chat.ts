import apiClient from './config';
import {
  ApiResponse,
  Pageable,
  CreateSessionRequest,
  CreateSessionResponse,
  SessionInfoResponse,
  UpdateSessionTitleRequest,
  ChatHistoryResponse,
  ChatTitleResponse,
  ChatParams,
  SessionListParams,
} from './types';

export class ChatAPI {
  /**
   * 智能体对话（流式输出）
   */
  static async chat(params: ChatParams): Promise<any> {
    const response = await apiClient.get('/api/v1/chat', {
      params,
      responseType: 'stream' // 对于流式输出
    });
    return response;
  }

  /**
   * 创建会话
   */
  static async createSession(data: CreateSessionRequest): Promise<ApiResponse<CreateSessionResponse>> {
    const response = await apiClient.post<ApiResponse<CreateSessionResponse>>('/api/v1/sessions', data);
    return response.data;
  }

  /**
   * 会话列表
   */
  static async getSessions(params?: SessionListParams): Promise<ApiResponse<Pageable<SessionInfoResponse>>> {
    const response = await apiClient.get<ApiResponse<Pageable<SessionInfoResponse>>>('/api/v1/sessions', { params });
    return response.data;
  }

  /**
   * 生成会话标题
   */
  static async generateSessionTitle(session_id: string): Promise<ApiResponse<ChatTitleResponse>> {
    const response = await apiClient.post<ApiResponse<ChatTitleResponse>>(`/api/v1/sessions/${session_id}/generate-title`);
    return response.data;
  }

  /**
   * 更新会话标题
   */
  static async updateSessionTitle(session_id: string, data: UpdateSessionTitleRequest): Promise<ApiResponse<null>> {
    const response = await apiClient.put<ApiResponse<null>>(`/api/v1/sessions/${session_id}/title`, data);
    return response.data;
  }

  /**
   * 删除会话
   */
  static async deleteSession(session_id: string): Promise<ApiResponse<null>> {
    const response = await apiClient.delete<ApiResponse<null>>(`/api/v1/sessions/${session_id}`);
    return response.data;
  }

  /**
   * 聊天记录
   */
  static async getSessionMessages(session_id: string): Promise<ApiResponse<ChatHistoryResponse>> {
    const response = await apiClient.get<ApiResponse<ChatHistoryResponse>>(`/api/v1/sessions/${session_id}/messages`);
    return response.data;
  }
}

export default ChatAPI;