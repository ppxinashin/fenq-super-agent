import apiClient from './config';
import {
  ApiResponse,
  Pageable,
  UserInfo,
  UserCreateRequest,
  UserUpdateRequest,
  UserListItem,
  UserListParams,
  MemorySettingRequest,
  MemorySettingResponse,
} from './types';

export class UsersAPI {
  /**
   * 创建新用户
   */
  static async createUser(data: UserCreateRequest): Promise<ApiResponse<UserInfo>> {
    const response = await apiClient.post<ApiResponse<UserInfo>>('/api/v1/users', data);
    return response.data;
  }

  /**
   * 修改用户信息
   */
  static async updateUser(data: UserUpdateRequest): Promise<ApiResponse<UserInfo>> {
    const response = await apiClient.put<ApiResponse<UserInfo>>('/api/v1/users', data);
    return response.data;
  }

  /**
   * 分页查询用户列表
   */
  static async getUserList(params?: UserListParams): Promise<ApiResponse<Pageable<UserListItem>>> {
    const response = await apiClient.get<ApiResponse<Pageable<UserListItem>>>('/api/v1/users', { params });
    return response.data;
  }

  /**
   * 获取用户详情
   */
  static async getUserById(user_id: string): Promise<ApiResponse<UserInfo>> {
    const response = await apiClient.get<ApiResponse<UserInfo>>(`/api/v1/users/${user_id}`);
    return response.data;
  }

  /**
   * 删除用户
   */
  static async deleteUser(user_id: string): Promise<ApiResponse<boolean>> {
    const response = await apiClient.delete<ApiResponse<boolean>>(`/api/v1/users/${user_id}`);
    return response.data;
  }

  /**
   * 查询长期记忆状态
   */
  static async getMemorySetting(): Promise<ApiResponse<boolean>> {
    const response = await apiClient.get<ApiResponse<boolean>>('/api/v1/memory-setting');
    return response.data;
  }

  /**
   * 设置长期记忆开关
   */
  static async setMemorySetting(data: MemorySettingRequest): Promise<ApiResponse<MemorySettingResponse>> {
    const response = await apiClient.post<ApiResponse<MemorySettingResponse>>('/api/v1/memory-setting', data);
    return response.data;
  }

  /**
   * 手动同步长期记忆
   */
  static async syncMemory(): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>('/api/v1/memory-sync');
    return response.data;
  }
}

export default UsersAPI;