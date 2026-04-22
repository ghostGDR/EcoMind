#!/bin/bash
# Henry AI 电商专家系统启动脚本

echo "🚀 启动 Henry AI 电商专家系统..."
echo ""
echo "📋 检查配置："
echo "  - oMLX 服务: http://127.0.0.1:8000"
echo "  - FastAPI 服务: http://localhost:8080"
echo "  - 模型: Qwen3-Coder-30B-A3B-Instruct-4bit"
echo ""

# 检查 oMLX 是否运行
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ oMLX 服务正在运行"
else
    echo "❌ oMLX 服务未运行，请先启动 oMLX"
    echo "   启动命令: /Applications/oMLX.app/Contents/MacOS/omlx-cli launch"
    exit 1
fi

echo ""
echo "🌐 启动 FastAPI 服务器..."
echo "   访问地址: http://localhost:8080"
echo "   API 文档: http://localhost:8080/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

cd "$(dirname "$0")"
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
