// 可用工具集常量

export interface ToolInfo {
  name: string;
  description: string;
}

export const AVAILABLE_TOOLS: Record<string, ToolInfo> = {
  web_scraper: {
    name: "网页抓取",
    description: "快速捕获当前网页完整快照，留存页面内容与结构"
  },
  calculator: {
    name: "计算器",
    description: "支持加减乘除等各类数字计算，精准输出结果"
  },
  rag: {
    name: "RAG检索",
    description: "从预设知识库中高效检索相关信息，提供精准知识支持"
  },
  web_search: {
    name: "网页搜索",
    description: "通过DuckDuckGo搜索引擎，全网检索所需网页信息"
  },
  now_time: {
    name: "当前时间",
    description: "获取当前精确日期与时间"
  }
}

// 获取工具列表（用于遍历）
export const getToolsList = (): Array<{ key: string; name: string; description: string }> => {
  return Object.entries(AVAILABLE_TOOLS).map(([key, tool]) => ({
    key,
    name: tool.name,
    description: tool.description
  }))
}

// 获取工具名称
export const getToolName = (toolKey: string): string => {
  return AVAILABLE_TOOLS[toolKey]?.name || toolKey
}

// 获取工具描述
export const getToolDescription = (toolKey: string): string => {
  return AVAILABLE_TOOLS[toolKey]?.description || ''
}

