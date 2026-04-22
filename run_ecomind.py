#!/usr/bin/env python3
"""
Henry AI 电商专家系统 - 启动脚本
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 启动 EcoMind AI 电商专家系统")
    print("=" * 60)
    print()
    print("📋 配置信息：")
    print(f"  - oMLX 服务: http://127.0.0.1:8000")
    print(f"  - FastAPI 服务: http://localhost:8080")
    print(f"  - 模型: {os.getenv('LLM_MODEL', 'Qwen3-Coder-30B-A3B-Instruct-4bit')}")
    print()
    print("🌐 访问地址：")
    print("  - 聊天界面: http://localhost:8080")
    print("  - API 文档: http://localhost:8080/docs")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8080,
        reload=False,
        log_level="info"
    )
