"""
PCB缺陷检测系统 - FastAPI 后端入口
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=5000,
        reload=True
    )
