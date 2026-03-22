#!/usr/bin/env python3
"""测试阿里百炼 API Key 是否有效"""

from openai import OpenAI

# 请输入你的 API Key
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # ← 在这里填写你的 Key

# 阿里百炼端点
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"

def test_api():
    print(f"🔑 测试 API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        
        # 尝试调用
        print("📡 正在调用 Qwen 模型...")
        response = client.chat.completions.create(
            model="qwen3.5-plus",
            messages=[
                {"role": "user", "content": "你好，请用一句话介绍你自己"}
            ],
            max_tokens=50
        )
        
        print("✅ API Key 有效！")
        print(f"\n模型回复：{response.choices[0].message.content}")
        print(f"\n使用模型：{response.model}")
        print(f"消耗 tokens: {response.usage}")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        print()
        print("可能的原因：")
        print("1. API Key 填写错误（请检查是否完整复制）")
        print("2. Key 未激活（登录控制台确认）")
        print("3. 账户余额不足")
        print("4. 网络问题")
        print()
        print("📖 详情：https://help.aliyun.com/zh/model-studio/error-code#apikey-error")

if __name__ == "__main__":
    test_api()
