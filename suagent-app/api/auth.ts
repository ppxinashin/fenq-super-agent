import apiClient from './config';
import {
  ApiResponse,
  RegisterRequest,
  RegisterResponse,
  LoginRequest,
  LoginResponse,
  LogoutResponse,
  ChangePasswordRequest,
  ChangePasswordResponse,
  TokenValidationResponse,
  UserInfo,
} from './types';

export class AuthAPI {
  /**
   * 用户注册
   */
  static async register(data: RegisterRequest): Promise<ApiResponse<RegisterResponse>> {
    const response = await apiClient.post<ApiResponse<RegisterResponse>>('/api/v1/auth/register', data);
    return response.data;
  }

  /**
   * 用户登录
   */
  static async login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    const response = await apiClient.post<ApiResponse<LoginResponse>>('/api/v1/auth/login', data);
    return response.data;
  }

  /**
   * 用户退出登录
   */
  static async logout(): Promise<ApiResponse<LogoutResponse>> {
    const response = await apiClient.post<ApiResponse<LogoutResponse>>('/api/v1/auth/logout');
    return response.data;
  }

  /**
   * 修改密码
   */
  static async changePassword(data: ChangePasswordRequest): Promise<ApiResponse<ChangePasswordResponse>> {
    const response = await apiClient.post<ApiResponse<ChangePasswordResponse>>('/api/v1/auth/change-password', data);
    return response.data;
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<ApiResponse<UserInfo>> {
    const response = await apiClient.get<ApiResponse<UserInfo>>('/api/v1/auth/me');
    return response.data;
  }

  /**
   * 验证token是否有效
   */
  static async validateToken(): Promise<ApiResponse<TokenValidationResponse>> {
    const response = await apiClient.post<ApiResponse<TokenValidationResponse>>('/api/v1/auth/validate-token');
    return response.data;
  }

  /**
   * 刷新访问令牌
   */
  static async refreshToken(): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>('/api/v1/auth/refresh-token');
    return response.data;
  }

  /**
   * 认证服务健康检查
   */
  static async healthCheck(): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.get<ApiResponse<Record<string, any>>>('/api/v1/auth/health');
    return response.data;
  }
}

export default AuthAPI;