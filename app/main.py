"""
操作系统原理课程"文件管理"章节 AI 伴学智能体
FastAPI 主应用入口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag import RAGSystem

app = FastAPI(
    title="操作系统文件管理 AI 伴学智能体",
    description="基于 RAG 的文件管理章节知识问答系统",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 RAG 系统
rag_system: Optional[RAGSystem] = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化 RAG 系统"""
    global rag_system
    knowledge_base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "knowledge_base"
    )
    rag_system = RAGSystem(knowledge_base_path)
    rag_system.initialize()


class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str
    top_k: int = 3


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    sources: list
    confidence: float


class ChapterInfo(BaseModel):
    """章节信息模型"""
    chapter_id: str
    title: str
    sections: list


@app.get("/", tags=["根路径"])
async def root():
    """根路径，返回欢迎信息"""
    return {
        "message": "欢迎使用操作系统文件管理 AI 伴学智能体",
        "description": "本智能体可以帮助您学习文件管理章节的知识点",
        "endpoints": {
            "query": "POST /query - 提问关于文件管理的问题",
            "chapters": "GET /chapters - 获取章节目录",
            "health": "GET /health - 健康检查"
        }
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "rag_initialized": rag_system is not None and rag_system.is_initialized()
    }


@app.get("/chapters", tags=["章节信息"], response_model=list[ChapterInfo])
async def get_chapters():
    """获取所有章节信息"""
    chapters = [
        ChapterInfo(
            chapter_id="01",
            title="文件与文件系统",
            sections=[
                "文件的定义、文件类型、文件属性",
                "文件系统的功能、层次结构"
            ]
        ),
        ChapterInfo(
            chapter_id="02",
            title="文件结构",
            sections=[
                "逻辑结构：无结构文件（流式文件）、有结构文件（记录式文件）",
                "物理结构：连续分配、链接分配、索引分配、多级索引分配"
            ]
        ),
        ChapterInfo(
            chapter_id="03",
            title="目录管理",
            sections=[
                "文件控制块（FCB）、索引节点（inode）",
                "单级目录、两级目录、多级目录（树形目录）",
                "绝对路径、相对路径",
                "目录查询技术、目录操作"
            ]
        ),
        ChapterInfo(
            chapter_id="04",
            title="文件存储空间管理",
            sections=[
                "空闲表法、空闲链表法、位示图法、成组链接法"
            ]
        ),
        ChapterInfo(
            chapter_id="05",
            title="文件共享与保护",
            sections=[
                "文件共享方式：基于索引节点、基于符号链",
                "文件保护：访问控制、口令、加密",
                "文件权限管理"
            ]
        ),
        ChapterInfo(
            chapter_id="06",
            title="文件操作与可靠性",
            sections=[
                "基本文件操作：创建、删除、读、写、打开、关闭",
                "文件备份、文件恢复机制"
            ]
        )
    ]
    return chapters


@app.post("/query", tags=["知识问答"], response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """
    提问关于文件管理章节的问题
    
    - **question**: 用户的问题
    - **top_k**: 返回最相关的知识片段数量（默认 3）
    """
    if not rag_system or not rag_system.is_initialized():
        raise HTTPException(
            status_code=503,
            detail="RAG 系统尚未初始化完成，请稍后重试"
        )
    
    try:
        result = rag_system.query(request.question, request.top_k)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询失败：{str(e)}"
        )


@app.get("/knowledge/{chapter_id}", tags=["知识库"])
async def get_knowledge(chapter_id: str):
    """获取指定章节的知识内容"""
    if not rag_system or not rag_system.is_initialized():
        raise HTTPException(
            status_code=503,
            detail="RAG 系统尚未初始化完成"
        )
    
    chapter_map = {
        "01": "文件与文件系统",
        "02": "文件结构",
        "03": "目录管理",
        "04": "文件存储空间管理",
        "05": "文件共享与保护",
        "06": "文件操作与可靠性"
    }
    
    if chapter_id not in chapter_map:
        raise HTTPException(
            status_code=404,
            detail=f"未找到章节 {chapter_id}，可选章节：{list(chapter_map.keys())}"
        )
    
    content = rag_system.get_chapter_content(chapter_id)
    
    return {
        "chapter_id": chapter_id,
        "title": chapter_map[chapter_id],
        "content": content
    }


@app.get("/chat", include_in_schema=False)
async def chat_page():
    """聊天页面"""
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    return FileResponse(os.path.join(static_path, "index.html"))


@app.get("/", include_in_schema=False)
async def root_redirect():
    """根路径重定向到聊天页面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/chat")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
