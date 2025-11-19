// MCP配置验证工具

interface McpServerConfig {
  type: string;
  url: string;
  [key: string]: any;
}

/**
 * 验证MCP服务器配置格式
 * @param configStr MCP配置JSON字符串
 * @returns { valid: boolean, error?: string }
 */
export function validateMcpConfig(configStr: string): { valid: boolean; error?: string } {
  // 空字符串或"{}"视为有效
  if (!configStr.trim() || configStr.trim() === '{}') {
    return { valid: true }
  }

  try {
    // 1. 验证是否为有效的JSON
    const config = JSON.parse(configStr)

    // 2. 验证是否为对象（不能是数组或其他类型）
    if (typeof config !== 'object' || config === null || Array.isArray(config)) {
      return { valid: false, error: 'MCP配置必须是一个JSON对象' }
    }

    // 3. 验证每个服务器配置
    const serverNames = Object.keys(config)
    
    if (serverNames.length === 0) {
      return { valid: true } // 空对象也是有效的
    }

    for (const serverName of serverNames) {
      const serverConfig = config[serverName]

      // 3.1 验证服务器配置是否为对象
      if (typeof serverConfig !== 'object' || serverConfig === null || Array.isArray(serverConfig)) {
        return { 
          valid: false, 
          error: `服务器 "${serverName}" 的配置必须是一个对象` 
        }
      }

      // 3.2 验证必须包含 type 字段
      if (!serverConfig.type) {
        return { 
          valid: false, 
          error: `服务器 "${serverName}" 缺少必填字段 "type"` 
        }
      }

      // 3.3 验证 type 必须为 "sse"
      if (serverConfig.type !== 'sse') {
        return { 
          valid: false, 
          error: `服务器 "${serverName}" 的 type 必须为 "sse"，当前为 "${serverConfig.type}"` 
        }
      }

      // 3.4 验证必须包含 url 字段
      if (!serverConfig.url) {
        return { 
          valid: false, 
          error: `服务器 "${serverName}" 缺少必填字段 "url"` 
        }
      }

      // 3.5 验证 url 格式
      if (typeof serverConfig.url !== 'string') {
        return { 
          valid: false, 
          error: `服务器 "${serverName}" 的 url 必须是字符串` 
        }
      }

      // 3.6 验证 url 是否为有效的URL格式
      try {
        new URL(serverConfig.url)
      } catch (e) {
        return { 
          valid: false, 
          error: `服务器 "${serverName}" 的 url 格式无效: ${serverConfig.url}` 
        }
      }
    }

    return { valid: true }

  } catch (e: any) {
    return { 
      valid: false, 
      error: `JSON格式错误: ${e.message}` 
    }
  }
}

/**
 * 格式化MCP配置（美化JSON）
 * @param configStr MCP配置JSON字符串
 * @returns 格式化后的JSON字符串
 */
export function formatMcpConfig(configStr: string): string {
  try {
    const config = JSON.parse(configStr)
    return JSON.stringify(config, null, 2)
  } catch (e) {
    return configStr
  }
}

