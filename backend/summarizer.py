#!/usr/bin/env python3
"""
视频内容总结器
使用 LLM 对字幕内容进行结构化总结
"""

import os
from typing import Optional

# 尝试导入 OpenAI 兼容的 SDK（支持 Bailian/阿里百炼等）
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


SUMMARIZE_PROMPT = """你是一位专业的学习笔记整理助手。请根据以下视频字幕内容，整理一份结构化的学习笔记。

要求：
1. 用 Markdown 格式输出
2. 包含以下部分：
   - # 视频标题
   - ## 📌 核心要点（3-5 个关键点）
   - ## 📖 详细内容（按逻辑分段，不是按时间）
   - ## 💡 关键概念/术语（如果有）
   - ## 💭 思考与启发（可选）
3. 语言：中文
4. 风格：像大学生上课记的笔记，清晰、有条理、便于复习
5. 如果内容中有代码示例，用代码块标注
6. 如果内容太短或无意义，如实告知

字幕内容：
{subtitle}

请开始整理笔记：
"""


def summarize_content(title: str, subtitle_text: str, api_key: Optional[str] = None, model: str = "qwen3.5-plus") -> str:
    """
    使用 LLM 总结视频内容
    
    Args:
        title: 视频标题
        subtitle_text: 字幕文本
        api_key: API Key（可选，如果为 None 则尝试从环境变量读取）
        model: 模型名称
    
    Returns:
        总结后的 Markdown 文本
    """
    if not OPENAI_AVAILABLE:
        return "❌ 未安装 openai 库，请运行：pip install openai"
    
    # 获取 API Key
    if not api_key:
        api_key = os.environ.get('DASHSCOPE_API_KEY') or os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        return "❌ 未找到 API Key，请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY 环境变量"
    
    try:
        # 使用阿里百炼（DashScope）的 OpenAI 兼容接口
        client = OpenAI(
            api_key=api_key,
            base_url="https://coding.dashscope.aliyuncs.com/v1"
        )
        
        # 截断过长的字幕（避免 token 超限）
        max_chars = 15000
        if len(subtitle_text) > max_chars:
            subtitle_text = subtitle_text[:max_chars] + "...（内容过长，已截断）"
        
        prompt = SUMMARIZE_PROMPT.format(subtitle=subtitle_text)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位专业的学习笔记整理助手，擅长将视频内容整理成结构化的笔记。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        summary = response.choices[0].message.content
        
        # 添加标题
        result = f"# {title}\n\n> 📺 视频学习笔记\n\n{summary}"
        
        return result
        
    except Exception as e:
        return f"❌ 总结失败：{str(e)}"


if __name__ == "__main__":
    # 测试
    test_title = "测试视频"
    test_subtitle = "这是一个测试字幕内容，用于验证总结功能是否正常工作。"
    result = summarize_content(test_title, test_subtitle)
    print(result)
