# 操作系统文件管理 AI 伴学智能体

基于 RAG（检索增强生成）技术的操作系统原理课程"文件管理"章节 AI 伴学智能体。

## 功能特点

- 📚 **完整知识库**：涵盖文件管理章节全部 6 个知识点
- 🔍 **智能检索**：基于关键词和相关性的混合检索算法
- 💬 **自然问答**：支持自然语言提问
- 📖 **来源追溯**：回答附带知识点来源
- 🚀 **快速部署**：支持 Docker 容器化和 Render 云部署

## 知识目录

```
6.1 文件与文件系统
  - 文件的定义、文件类型、文件属性
  - 文件系统的功能、层次结构

6.2 文件结构
  - 逻辑结构：无结构文件（流式文件）、有结构文件（记录式文件）
  - 物理结构：连续分配、链接分配、索引分配、多级索引分配

6.3 目录管理
  - 文件控制块（FCB）、索引节点（inode）
  - 单级目录、两级目录、多级目录（树形目录）
  - 绝对路径、相对路径
  - 目录查询技术、目录操作

6.4 文件存储空间管理
  - 空闲表法、空闲链表法、位示图法、成组链接法

6.5 文件共享与保护
  - 文件共享方式：基于索引节点、基于符号链
  - 文件保护：访问控制、口令、加密
  - 文件权限管理

6.6 文件操作与可靠性
  - 基本文件操作：创建、删除、读、写、打开、关闭
  - 文件备份、文件恢复机制
```

## 本地运行

### 环境要求

- Python 3.10+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 访问接口

打开浏览器访问：http://localhost:8000/docs

## API 接口

### 1. 健康检查

```bash
GET /health
```

### 2. 获取章节目录

```bash
GET /chapters
```

### 3. 知识问答

```bash
POST /query
Content-Type: application/json

{
  "question": "什么是 inode？",
  "top_k": 3
}
```

响应示例：

```json
{
  "answer": "根据文件管理章节的知识库内容，为您解答：...",
  "sources": [
    {
      "chapter": "第三章 目录管理",
      "section": "索引节点（inode）",
      "relevance": 8.5
    }
  ],
  "confidence": 0.85
}
```

### 4. 获取章节内容

```bash
GET /knowledge/{chapter_id}
```

## Docker 部署

### 构建镜像

```bash
docker build -t os-file-system-agent .
```

### 运行容器

```bash
docker run -d -p 8000:8000 --name os-agent os-file-system-agent
```

## Render 部署

### 步骤

1. 将代码推送到 GitHub 仓库

2. 登录 [Render](https://render.com)

3. 创建新的 Web Service

4. 连接 GitHub 仓库

5. 配置：
   - 环境：Docker
   - 构建命令：自动检测
   - 启动命令：自动检测

6. 部署

### render.yaml

项目包含 `render.yaml` 配置文件，支持一键部署。

## 项目结构

```
os-file-system-agent/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 主应用
│   └── rag.py           # RAG 检索系统
├── knowledge_base/
│   ├── 01_文件与文件系统.md
│   ├── 02_文件结构.md
│   ├── 03_目录管理.md
│   ├── 04_文件存储空间管理.md
│   ├── 05_文件共享与保护.md
│   └── 06_文件操作与可靠性.md
├── tests/
├── Dockerfile
├── render.yaml
├── requirements.txt
└── README.md
```

## 使用示例

### Python 客户端

```python
import requests

# 提问
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "连续分配和链接分配有什么区别？"}
)

result = response.json()
print(result["answer"])
print("来源:", result["sources"])
```

### cURL

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是位示图法？"}'
```

## 注意事项

- 知识库内容基于通用操作系统原理教材整理
- 具体实现可能因操作系统而异
- 如知识库中暂无相关内容，会提示"请咨询老师"

## License

MIT License
