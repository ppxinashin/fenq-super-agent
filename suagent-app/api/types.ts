// Base API Response Types
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface Pageable<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Auth Types
export interface RegisterRequest {
  username: string;
  password: string;
  confirm_password: string;
}

export interface RegisterResponse {
  user_id: number;
  username: string;
  role: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export interface LogoutResponse {
  message: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export interface ChangePasswordResponse {
  message: string;
}

export interface TokenValidationResponse {
  valid: boolean;
  user_id?: number;
  username?: string;
}

// User Types
export interface UserInfo {
  user_id: bigint;  // 使用 bigint 处理雪花号
  username: string;
  role: string;
  is_deleted?: boolean;
  created_at: string;
  created_by?: string;
  updated_at?: string;
}

export interface UserCreateRequest {
  username: string;
  password: string;
  role: string;
}

export interface UserUpdateRequest {
  user_id: string;  // 改为string避免BigInt序列化问题
  password?: string;
  role?: string;
}

export interface UserListItem {
  user_id: bigint;  // 使用 bigint 处理雪花号
  username: string;
  role: string;
  created_at: string;
  updated_at?: string;
}

export interface MemorySettingRequest {
  enabled: boolean;
}

export interface MemorySettingResponse {
  enabled: boolean;
  message: string;
}

// Agent Types
export interface AgentCreateRequest {
  agent_id: string;
  agent_name: string;
  description?: string;
  system_prompt?: string;
  tools?: string[];
  mcp_status?: boolean;
  mcp_config?: string;
}

export interface AgentCreateResponse {
  agent_id: string;
  agent_name: string;
}

export interface AgentUpdateRequest {
  agent_id: string;
  agent_name?: string;
  description?: string;
  system_prompt?: string;
  tools?: string[];
  mcp_status?: boolean;
  mcp_config?: string;
}

export interface AgentToolsUpdateRequest {
  agent_id: string;
  tools: string[];
}

export interface AgentMcpUpdateRequest {
  agent_id: string;
  mcp_status: boolean;
  mcp_config: string;
}

export interface AgentUpdateResponse {
  agent_id: string;
  agent_name: string;
  updated: boolean;
}

export interface AgentDeleteResponse {
  agent_id: string;
  deleted: boolean;
}

export interface AgentInfo {
  agent_id: string;
  agent_name: string;
  description: string;
  system_prompt: string;
  tools: string[];
  mcp_status: boolean;
  mcp_config?: string;
  creator_id: number;
  creator_username: string;
  created_at: string;
  updated_by_id?: number;
  updated_by_username?: string;
  updated_at?: string;
}

export interface AgentSimpleInfo {
  agent_id: string;
  agent_name: string;
  description: string;
  creator_username: string;
  created_at: string;
}

export interface AgentListItem {
  agent_id: string;
  agent_name: string;
  description: string;
  creator_username: string;
  creator_id: number;
  created_at: string;
  updated_at?: string;
  is_deleted: boolean;
}

// Session Types
export interface CreateSessionRequest {
  agent_id: string;
}

export interface CreateSessionResponse {
  session_id: string;
  agent_id: string;
  title: string;
}

export interface SessionInfoResponse {
  session_id: string;
  agent_id: string;
  agent_name: string;
  title: string;
  created_at: string;
  last_message_at?: string;
  message_count: number;
}

export interface UpdateSessionTitleRequest {
  title: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ChatTitleResponse {
  session_id: string;
  title: string;
}

// File Types
export interface FileUploadResponse {
  filename: string;
  source: string;
  size: number;
  content_type: string;
  message: string;
}

export interface FileInfo {
  file_name: string;
  source: string;
  file_size: number;
  content_type: string;
  total_chunks: number;
  status: string;
  author: string;
  minio_bucket: string;
  created_at: string;
  updated_at: string;
}

export interface FileListResponse {
  page: number;
  page_size: number;
  total: number;
  data: FileInfo[];
}

export interface FileChunksResponse {
  filename: string;
  source: string;
  chunk_count: number;
  chunks: FileChunk[];
}

export interface FileChunk {
  chunk_index: number;
  content: string;
  metadata?: any;
}

export interface FileDeleteResponse {
  source: string;
  deleted: boolean;
  message: string;
}

export interface FileBatchDeleteRequest {
  agent_id: string;
  sources: string[];
}

export interface FileBatchDeleteResponse {
  results: FileDeleteResult[];
}

export interface FileDeleteResult {
  source: string;
  deleted: boolean;
  message?: string;
}

// Query Parameters
export interface PaginationParams {
  page?: number;
  page_size?: number;
  keyword?: string;
}

export interface UserListParams extends PaginationParams {}

export interface AgentListParams extends PaginationParams {}

export interface AgentCardListParams extends PaginationParams {}

export interface SessionListParams extends PaginationParams {
  agent_id?: string;
}

export interface FileListParams {
  agent_id: string;
  page?: number;
  page_size?: number;
  keyword?: string;
}

export interface ChatParams {
  agent_id: string;
  session_id: number;
  message: string;
}

export interface FileChunkParams {
  agent_id: string;
  source: string;
}

export interface FileDeleteParams {
  agent_id: string;
  source: string;
}

export interface AgentHealthParams {
  m?: string;
}