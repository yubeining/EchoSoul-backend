#!/usr/bin/env python3
"""
获取用户token脚本
用于WebSocket测试的认证
"""

import asyncio
import sys
import os
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def get_user_token():
    """获取用户token"""
    print("🔑 获取用户token")
    print("=" * 40)
    
    # 用户登录信息
    login_data = {
        "username": "13357753818",
        "password": "suda4008"
    }
    
    try:
        # 发送登录请求
        response = requests.post(
            "http://localhost:8080/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析结果: {result}")
            if result.get("code") == 1:  # 登录成功
                token = result.get("data", {}).get("token")
                user_info = result.get("data", {}).get("userInfo")
                
                print(f"✅ 登录成功")
                print(f"   用户ID: {user_info.get('id')}")
                print(f"   用户名: {user_info.get('username')}")
                print(f"   昵称: {user_info.get('nickname')}")
                print(f"   Token: {token[:50]}...")
                
                return token, user_info
            else:
                print(f"❌ 登录失败: {result.get('msg')}")
                return None, None
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ 获取token异常: {str(e)}")
        return None, None

async def main():
    """主函数"""
    token, user_info = await get_user_token()
    
    if token:
        print(f"\n🎉 成功获取用户token!")
        print(f"Token: {token}")
        
        # 保存token到文件
        with open("user_token.txt", "w") as f:
            f.write(token)
        print(f"Token已保存到: user_token.txt")
    else:
        print(f"\n❌ 获取用户token失败")

if __name__ == "__main__":
    asyncio.run(main())
