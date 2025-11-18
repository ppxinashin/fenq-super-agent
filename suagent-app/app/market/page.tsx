'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { FaJava, FaBug, FaPython, FaLinux, FaLanguage, FaFileAlt, FaTools, FaChartBar, FaSearch, FaSpinner } from 'react-icons/fa'
import Footer from '@/components/Footer'
import { toast } from 'react-hot-toast'

interface Agent {
  id: string
  name: string
  description: string
  author: string
  icon: string
  color: string
  category: string
}

const mockAgents: Agent[] = [
  {
    id: 'java',
    name: 'Java架构师',
    description: '一位全能的资深 Java 技术专家，助力解决各类技术难题',
    author: '@悠闲葛优躺',
    icon: 'J',
    color: 'from-orange-400 to-red-500',
    category: '编程开发'
  },
  {
    id: 'debug',
    name: '代码 Debug',
    description: '能助您分析代码、优化性能、解答编程疑问的智能助手',
    author: '@斑马在海边',
    icon: 'D',
    color: 'from-blue-400 to-purple-500',
    category: '编程开发'
  },
  {
    id: 'python',
    name: 'Python专家',
    description: '一位精通 Python3 且耐心友好的问题解决专家',
    author: '@system',
    icon: 'P',
    color: 'from-green-400 to-blue-500',
    category: '编程开发'
  },
  {
    id: 'linux',
    name: 'Linux系统',
    description: '便于快速的学习Linux操作系统与应用这门课程',
    author: '@vbgood',
    icon: 'L',
    color: 'from-gray-400 to-black',
    category: '系统运维'
  },
  {
    id: 'translate',
    name: '技术翻译助手',
    description: '精通技术文档中英翻译与写作，提供专业服务的智能助手',
    author: '@加号蛙',
    icon: '翻',
    color: 'from-purple-400 to-pink-500',
    category: '翻译工具'
  },
  {
    id: 'patent',
    name: '专利技术交底书',
    description: '专业辅助撰写专利交底书，高效精准，遵循流程规范',
    author: '@大强哥',
    icon: '专',
    color: 'from-yellow-400 to-orange-500',
    category: '文档写作'
  },
  {
    id: 'work',
    name: '工作处理助手',
    description: '能助您解决各类工作难题，优化流程提效率的助手',
    author: '@我的id配享太庙',
    icon: '工',
    color: 'from-teal-400 to-green-500',
    category: '工作效率'
  },
  {
    id: 'report',
    name: '工作成果汇报',
    description: '能为您撰写客观全面的绩效自评，分点展示工作详情',
    author: '@柠檬绿冰可乐',
    icon: '汇',
    color: 'from-indigo-400 to-blue-500',
    category: '文档写作'
  }
]

// 检测是否为移动端
const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 1024
}

export default function MarketPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [agents, setAgents] = useState<Agent[]>(mockAgents)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  useEffect(() => {
    filterAgents()
  }, [searchTerm])

  const filterAgents = () => {
    let filtered = mockAgents

    if (searchTerm) {
      filtered = filtered.filter(agent =>
        agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setAgents(filtered)
  }

  const handleAgentClick = (agentId: string) => {
    const agent = mockAgents.find(a => a.id === agentId)

    // 统一显示加载提示
    toast.success(`正在加载 ${agent?.name}...`)

    if (isMobile()) {
      // 移动端：直接创建新session并跳转到聊天页面
      const sessionId = Date.now().toString()
      setTimeout(() => {
        router.push(`/chat/${agentId}/${sessionId}`)
      }, 300)
    } else {
      // 桌面端：跳转到智能体框架页面
      setTimeout(() => {
        router.push(`/chat/${agentId}`)
      }, 500)
    }
  }

  const handleLoadMore = () => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      toast.success('已加载更多智能体')
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header/>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">发现 AI 智能体</h2>
          <p className="text-gray-600">探索丰富的智能体生态，找到适合你的AI助手</p>
        </div>

        {/* 搜索框 */}
        <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
          <div className="max-w-2xl">
            <div className="flex shadow-lg rounded-lg overflow-hidden">
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <FaSearch className="text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-inset-0"
                  placeholder="搜索智能体..."
                />
              </div>
              <button className="px-6 py-3 bg-indigo-600 text-white hover:bg-indigo-700 transition-colors duration-200 flex items-center focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-inset-0">
                <FaSearch className="mr-2" />
                搜索
              </button>
            </div>
          </div>
        </div>

        {/* 智能体网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {agents.map((agent, index) => (
            <div
              key={agent.id}
              onClick={() => handleAgentClick(agent.id)}
              className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-xl hover:-translate-y-2 transition-all duration-300 cursor-pointer group"
            >
              <div className={`w-16 h-16 bg-gradient-to-r ${agent.color} rounded-2xl flex items-center justify-center mb-4 text-white text-2xl font-bold group-hover:scale-110 transition-transform duration-300`}>
                {agent.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">
                {agent.name}
              </h3>
              <p className="text-gray-600 text-sm mb-4 line-clamp-2 overflow-hidden">
                {agent.description}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{agent.author}</span>
              </div>
            </div>
          ))}
        </div>

        {/* 加载更多 */}
        <div className="mt-12 text-center">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="px-8 py-3 border border-gray-300 rounded-xl text-gray-600 hover:bg-gray-50 hover:border-gray-400 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center mx-auto space-x-2"
          >
            {loading ? (
              <>
                <FaSpinner className="animate-spin" />
                <span>加载中...</span>
              </>
            ) : (
              <>
                <FaSpinner />
                <span>加载更多</span>
              </>
            )}
          </button>
        </div>
      </main>

      <Footer />
    </div>
  )
}