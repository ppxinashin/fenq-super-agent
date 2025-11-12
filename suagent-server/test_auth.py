#!/home/ubuntu/miniconda3/envs/suagent-server/bin/python
"""
用户认证功能测试脚本 - 在suagent-server conda环境中运行
"""

import os
import sys
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import aiohttp
import json
from typing import Optional

# 测试配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class AuthTester:
    """认证功能测试器"""

    def __init__(self):
        self.session = None
        self.access_token = None
        self.user_info = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def register_user(self, username: str, password: str) -> dict:
        """测试用户注册"""
        print(f"\n🔧 测试用户注册: {username}")

        data = {
            "username": username,
            "password": password,
            "confirm_password": password
        }

        async with self.session.post(f"{API_BASE}/auth/register", json=data) as response:
            result = await response.json()

            if response.status == 200:
                print(f"✅ 注册成功: {result}")
                return result
            else:
                print(f"❌ 注册失败: {result}")
                return result

    async def login_user(self, username: str, password: str) -> Optional[dict]:
        """测试用户登录"""
        print(f"\n🔑 测试用户登录: {username}")

        data = {
            "username": username,
            "password": password
        }

        async with self.session.post(f"{API_BASE}/auth/login", json=data) as response:
            result = await response.json()

            if response.status == 200:
                self.access_token = result["result"]["access_token"]
                self.user_info = result["result"]["user_info"]
                print(f"✅ 登录成功: token已保存")
                return result
            else:
                print(f"❌ 登录失败: {result}")
                return None

    async def get_current_user(self) -> dict:
        """测试获取当前用户信息"""
        print(f"\n👤 测试获取当前用户信息")

        if not self.access_token:
            print("❌ 未登录，无法获取用户信息")
            return {}

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with self.session.get(f"{API_BASE}/auth/me", headers=headers) as response:
            result = await response.json()

            if response.status == 200:
                print(f"✅ 获取用户信息成功: {result['result']['username']}")
                return result
            else:
                print(f"❌ 获取用户信息失败: {result}")
                return result

    async def validate_token(self) -> dict:
        """测试Token验证"""
        print(f"\n🔍 测试Token验证")

        if not self.access_token:
            print("❌ 未登录，无法验证token")
            return {}

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with self.session.post(f"{API_BASE}/auth/validate-token", headers=headers) as response:
            result = await response.json()

            if response.status == 200:
                print(f"✅ Token验证成功: 有效={result['result']['valid']}")
                return result
            else:
                print(f"❌ Token验证失败: {result}")
                return result

    async def logout_user(self) -> dict:
        """测试用户退出登录"""
        print(f"\n🚪 测试用户退出登录")

        if not self.access_token:
            print("❌ 未登录，无法退出")
            return {}

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with self.session.post(f"{API_BASE}/auth/logout", headers=headers) as response:
            result = await response.json()

            if response.status == 200:
                print(f"✅ 退出登录成功")
                self.access_token = None
                self.user_info = None
                return result
            else:
                print(f"❌ 退出登录失败: {result}")
                return result

    async def test_invalid_login(self) -> dict:
        """测试无效登录"""
        print(f"\n🚫 测试无效登录（错误密码）")

        data = {
            "username": "test_user",
            "password": "wrong_password"
        }

        async with self.session.post(f"{API_BASE}/auth/login", json=data) as response:
            result = await response.json()

            if response.status != 200:
                print(f"✅ 无效登录被正确拒绝: {result}")
                return result
            else:
                print(f"❌ 无效登录未被拒绝: {result}")
                return result

    async def test_unauthorized_access(self) -> dict:
        """测试未授权访问"""
        print(f"\n🔒 测试未授权访问（无token）")

        async with self.session.get(f"{API_BASE}/auth/me") as response:
            result = await response.json()

            if response.status != 200:
                print(f"✅ 未授权访问被正确拒绝: {response.status}")
                return result
            else:
                print(f"❌ 未授权访问未被拒绝: {result}")
                return result

    async def health_check(self) -> dict:
        """健康检查"""
        print(f"\n🏥 健康检查")

        async with self.session.get(f"{API_BASE}/auth/health") as response:
            result = await response.json()

            if response.status == 200:
                print(f"✅ 认证服务健康: {result['result']}")
                return result
            else:
                print(f"❌ 认证服务异常: {result}")
                return result

    async def run_full_test(self):
        """运行完整测试流程"""
        print("🚀 开始用户认证功能完整测试")
        print("=" * 60)

        test_username = "test_user_123"
        test_password = "test_password_123"

        try:
            # 1. 健康检查
            await self.health_check()

            # 2. 测试用户注册
            await self.register_user(test_username, test_password)

            # 3. 测试无效登录
            await self.test_invalid_login()

            # 4. 测试用户登录
            await self.login_user(test_username, test_password)

            # 5. 测试获取当前用户信息
            await self.get_current_user()

            # 6. 测试Token验证
            await self.validate_token()

            # 7. 测试未授权访问
            await self.test_unauthorized_access()

            # 8. 测试退出登录
            await self.logout_user()

            # 9. 退出后再测试访问
            await self.get_current_user()

            print("\n" + "=" * 60)
            print("🎉 用户认证功能测试完成")

        except Exception as e:
            print(f"\n❌ 测试过程中发生异常: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    print("请确保服务器正在运行: python src/main.py")
    print("等待3秒后开始测试...")
    await asyncio.sleep(3)

    async with AuthTester() as tester:
        await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())