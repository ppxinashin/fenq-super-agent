"""
API 客户端示例 - 展示如何调用 FastAPI 服务
"""

import requests
import json


def chat_example():
    """标准聊天示例"""
    
    url = "http://localhost:8000/api/agent/chat"
    
    payload = {
        "message": "你好，请介绍一下你自己",
        "session_id": "client_demo_001",
        "use_memory": False,
        "enable_tools": True,
    }
    
    print("=" * 60)
    print("发送聊天请求...")
    print(f"消息: {payload['message']}")
    print("=" * 60)
    print()
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"🤖 Agent 回复:")
        print(data["reply"])
        print()
        print(f"会话 ID: {data['session_id']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)


def chat_with_memory_example():
    """带记忆的聊天示例"""
    
    url = "http://localhost:8000/api/agent/chat"
    session_id = "memory_demo_001"
    
    messages = [
        "我叫李四",
        "我今年 30 岁",
        "你还记得我叫什么名字吗？",
    ]
    
    print("=" * 60)
    print("带记忆的聊天示例")
    print(f"会话 ID: {session_id}")
    print("=" * 60)
    print()
    
    for message in messages:
        print(f"👤 用户: {message}")
        
        payload = {
            "message": message,
            "session_id": session_id,
            "use_memory": True,
            "enable_tools": True,
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Agent: {data['reply']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
        
        print()
        print("-" * 60)
        print()


def stream_chat_example():
    """流式聊天示例"""
    
    url = "http://localhost:8000/api/agent/chat/stream"
    
    payload = {
        "message": "请用 100 字左右介绍一下人工智能",
        "session_id": "stream_demo_001",
        "enable_tools": False,
    }
    
    print("=" * 60)
    print("流式聊天示例")
    print(f"消息: {payload['message']}")
    print("=" * 60)
    print()
    print("🤖 Agent 回复 (流式):")
    
    response = requests.post(url, json=payload, stream=True)
    
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_str = line_str[6:]  # 移除 "data: " 前缀
                    
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        if "content" in data:
                            print(data["content"])
                        elif "error" in data:
                            print(f"❌ 错误: {data['error']}")
                    except json.JSONDecodeError:
                        pass
        print()
    else:
        print(f"❌ 请求失败: {response.status_code}")


def health_check():
    """健康检查"""
    
    url = "http://localhost:8000/api/health"
    
    print("=" * 60)
    print("健康检查")
    print("=" * 60)
    print()
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 服务运行正常")
        print(f"应用名称: {data['app_name']}")
        print(f"版本: {data['version']}")
        print(f"状态: {data['status']}")
        print(f"时间: {data['timestamp']}")
    else:
        print(f"❌ 健康检查失败: {response.status_code}")


def main():
    """主函数"""
    
    print("\n" + "=" * 60)
    print("Fenq Super Agent - API 客户端示例")
    print("=" * 60)
    print()
    
    # 1. 健康检查
    health_check()
    print("\n")
    
    # 2. 标准聊天
    chat_example()
    print("\n")
    
    # 3. 带记忆的聊天
    # chat_with_memory_example()
    # print("\n")
    
    # 4. 流式聊天
    # stream_chat_example()
    # print("\n")
    
    print("✅ 示例完成！")


if __name__ == "__main__":
    main()

