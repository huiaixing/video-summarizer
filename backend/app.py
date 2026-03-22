#!/usr/bin/env python3
"""
B 站视频总结器 - Flask 后端服务（Whisper 增强版）
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

from subtitle_extractor import extract_subtitle
from summarizer import summarize_content

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)


@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    处理视频总结请求
    
    Request JSON:
    {
        "url": "B 站视频链接",
        "api_key": "可选的 API Key",
        "use_whisper": true/false,
        "whisper_model": "tiny/base/small/medium/large"
    }
    
    Response JSON:
    {
        "success": true/false,
        "title": "视频标题",
        "summary": "总结内容（Markdown）",
        "message": "状态信息"
    }
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            "success": False,
            "message": "❌ 请提供视频链接"
        }), 400
    
    url = data.get('url', '').strip()
    api_key = data.get('api_key', None)
    use_whisper = data.get('use_whisper', True)
    whisper_model = data.get('whisper_model', 'tiny')
    
    if not url:
        return jsonify({
            "success": False,
            "message": "❌ 视频链接不能为空"
        }), 400
    
    # 1. 提取字幕（或 Whisper 转写）
    print(f"📥 正在处理：{url}")
    print(f"🔧 配置：Whisper={use_whisper}, 模型={whisper_model}")
    
    title, subtitle_text, extract_msg = extract_subtitle(
        url, 
        use_whisper=use_whisper, 
        whisper_model=whisper_model
    )
    
    print(f"📋 提取结果：{extract_msg}")
    
    if not subtitle_text:
        return jsonify({
            "success": False,
            "message": extract_msg
        }), 400
    
    # 2. 总结内容
    print("🤖 正在生成总结...")
    summary = summarize_content(title, subtitle_text, api_key)
    
    if summary.startswith("❌"):
        return jsonify({
            "success": False,
            "message": summary
        }), 500
    
    print("✅ 完成！")
    
    return jsonify({
        "success": True,
        "title": title,
        "summary": summary,
        "message": extract_msg
    })


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "bilibili-summarizer"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    
    print(f"🚀 启动服务：http://localhost:{port}")
    print(f"📁 前端页面：http://localhost:{port}/")
    print(f"📡 API 端点：http://localhost:{port}/api/summarize")
    print(f"🎤 Whisper 支持：已启用")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
