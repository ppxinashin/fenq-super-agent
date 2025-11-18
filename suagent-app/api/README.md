# Fenq Super Agent API 客户端

这是一个基于 TypeScript 和 axios 的完整 API 客户端，用于与 Fenq Super Agent 服务器进行交互。

## 安装依赖

确保项目已安装 axios：

```bash
npm install axios
# 或者
yarn add axios
```

## 使用方法

### 1. 导入 API 模块

```typescript
import {
  AuthAPI,
  UsersAPI,
  AgentsAPI,
  ChatAPI,
  FilesAPI,
  SystemAPI,
  apiClient
} from './api';
```

### 2. 配置环境变量

在 `.env.local` 文件中设置 API 基础 URL：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## API 模块说明

### 认证模块 (AuthAPI)

```typescript
// 用户注册
const registerResponse = await AuthAPI.register({
  username: 'testuser',
  password: 'password123',
  confirm_password: 'password123'
});

// 用户登录
const loginResponse = await AuthAPI.login({
  username: 'testuser',
  password: 'password123'
});

// 存储访问令牌
localStorage.setItem('access_token', loginResponse.data.access_token);

// 获取当前用户信息
const userInfo = await AuthAPI.getCurrentUser();

// 退出登录
await AuthAPI.logout();
```

### 用户管理模块 (UsersAPI)

```typescript
// 创建用户（需要管理员权限）
const newUser = await UsersAPI.createUser({
  username: 'newuser',
  password: 'password123',
  role: 'user'
});

// 获取用户列表
const userList = await UsersAPI.getUserList({
  page: 1,
  page_size: 20,
  keyword: 'search'
});

// 更新用户信息
await UsersAPI.updateUser({
  user_id: 123,
  role: 'admin'
});

// 设置长期记忆开关
await UsersAPI.setMemorySetting({
  enabled: true
});
```

### 智能体管理模块 (AgentsAPI)

```typescript
// 创建智能体
const agent = await AgentsAPI.createAgent({
  agent_id: 'web_assistant',
  agent_name: '网页助手',
  description: '专门处理网页相关任务的智能体',
  system_prompt: '你是一个专业的网页分析助手',
  tools: ['web_scraper', 'web_search'],
  mcp_status: false
});

// 获取智能体卡片列表
const agentCards = await AgentsAPI.getAgentCardList({
  page: 1,
  page_size: 20
});

// 获取智能体详情
const agentInfo = await AgentsAPI.getAgentById('web_assistant');

// 更新智能体工具
await AgentsAPI.updateAgentTools({
  agent_id: 'web_assistant',
  tools: ['web_scraper', 'web_search', 'file_reader']
});
```

### 聊天管理模块 (ChatAPI)

```typescript
// 创建会话
const session = await ChatAPI.createSession({
  agent_id: 'web_assistant'
});

// 智能体对话（流式输出）
const chatResponse = await ChatAPI.chat({
  agent_id: 'web_assistant',
  session_id: session.data.session_id,
  message: '你好，请帮我分析这个网页'
});

// 获取会话列表
const sessions = await ChatAPI.getSessions({
  page: 1,
  page_size: 20,
  agent_id: 'web_assistant'
});

// 生成会话标题
await ChatAPI.generateSessionTitle(session.data.session_id);

// 获取聊天记录
const messages = await ChatAPI.getSessionMessages(session.data.session_id);
```

### 文件管理模块 (FilesAPI)

```typescript
// 上传文件
const uploadResponse = await FilesAPI.uploadFile('web_assistant', file);

// 获取文件列表
const fileList = await FilesAPI.getFileList({
  agent_id: 'web_assistant',
  page: 1,
  page_size: 20
});

// 查看文件分块
const chunks = await FilesAPI.getFileChunks({
  agent_id: 'web_assistant',
  source: 'path/to/file.pdf'
});

// 删除文件
await FilesAPI.deleteFile({
  agent_id: 'web_assistant',
  source: 'path/to/file.pdf'
});

// 批量删除文件
await FilesAPI.batchDeleteFiles({
  agent_id: 'web_assistant',
  sources: ['file1.pdf', 'file2.docx']
});
```

### 系统模块 (SystemAPI)

```typescript
// 健康检查
const health = await SystemAPI.healthCheck();

// 智能体健康检测
const agentHealth = await SystemAPI.agentHealth({
  m: '测试消息'
});
```

## 错误处理

API 客户端自动处理认证错误（401），当 token 过期时会自动跳转到登录页面：

```typescript
import { apiClient } from './api';

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 类型定义

所有 API 请求和响应都有完整的 TypeScript 类型定义：

```typescript
import {
  ApiResponse,
  UserInfo,
  AgentInfo,
  ChatMessage,
  PaginationParams
} from './api/types';

// 使用类型定义
const userList: ApiResponse<Pageable<UserListItem>> = await UsersAPI.getUserList();
```

## 环境配置

- **开发环境**: `http://localhost:8000`
- **生产环境**: 通过 `NEXT_PUBLIC_API_BASE_URL` 环境变量配置

## 注意事项

1. **认证**: 大部分 API 需要在 Header 中提供 `Authorization: Bearer <token>`
2. **权限控制**: 某些操作需要特定角色权限
3. **流式输出**: 聊天接口使用流式输出，需要特殊处理
4. **文件上传**: 使用 `multipart/form-data` 格式
5. **分页参数**: 所有列表接口支持分页，默认每页 20 条记录