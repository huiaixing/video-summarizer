#!/bin/bash
# B 站视频总结器 - 启动脚本

cd "$(dirname "$0")/backend"

echo "🎬 B 站视频总结器"
echo "=================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python3"
    exit 1
fi

# 创建/激活虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt

echo ""
echo "🚀 启动服务..."
echo "📱 访问：http://localhost:5000"
echo "💡 按 Ctrl+C 停止服务"
echo ""

python3 app.py
