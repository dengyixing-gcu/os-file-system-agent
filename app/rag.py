"""
RAG (Retrieval-Augmented Generation) 检索增强生成系统
负责知识库的加载、索引和查询
"""

import os
import re
from typing import List, Dict, Optional, Any
from pathlib import Path


class RAGSystem:
    """
    简化的 RAG 系统实现
    使用基于关键词和语义的混合检索策略
    """
    
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.documents: List[Dict[str, Any]] = []
        self.index: Dict[str, List[int]] = {}
        self.initialized = False
        
    def initialize(self):
        """初始化 RAG 系统，加载知识库"""
        self._load_knowledge_base()
        self._build_index()
        self.initialized = True
        
    def is_initialized(self) -> bool:
        """检查系统是否已初始化"""
        return self.initialized
    
    def _load_knowledge_base(self):
        """加载知识库中的所有 Markdown 文件"""
        kb_path = Path(self.knowledge_base_path)
        
        if not kb_path.exists():
            raise FileNotFoundError(f"知识库路径不存在：{self.knowledge_base_path}")
        
        md_files = sorted(kb_path.glob("*.md"))
        
        for file_path in md_files:
            chapter_id = file_path.stem.split("_")[0]
            chapter_title = self._extract_chapter_title(file_path)
            
            content = file_path.read_text(encoding="utf-8")
            sections = self._split_into_sections(content, chapter_id, chapter_title)
            
            self.documents.extend(sections)
    
    def _extract_chapter_title(self, file_path: Path) -> str:
        """从文件内容中提取章节标题"""
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        for line in lines[:10]:
            if line.startswith("# "):
                return line[2:].strip()
        return file_path.stem
    
    def _split_into_sections(self, content: str, chapter_id: str, chapter_title: str) -> List[Dict]:
        """将文档内容分割成知识片段"""
        sections = []
        current_section = {"title": "", "content": [], "level": 0}
        
        lines = content.split("\n")
        current_heading = chapter_title
        
        for i, line in enumerate(lines):
            # 检测标题行
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match:
                # 保存之前的片段
                if current_section["content"]:
                    sections.append({
                        "chapter_id": chapter_id,
                        "chapter_title": chapter_title,
                        "section_title": current_heading,
                        "content": "\n".join(current_section["content"]),
                        "keywords": self._extract_keywords(current_section["content"])
                    })
                
                # 开始新片段
                level = len(heading_match.group(1))
                current_heading = heading_match.group(2)
                current_section = {
                    "title": current_heading,
                    "content": [],
                    "level": level
                }
            else:
                # 添加内容到当前片段
                if line.strip():
                    current_section["content"].append(line)
        
        # 保存最后一个片段
        if current_section["content"]:
            sections.append({
                "chapter_id": chapter_id,
                "chapter_title": chapter_title,
                "section_title": current_heading,
                "content": "\n".join(current_section["content"]),
                "keywords": self._extract_keywords(current_section["content"])
            })
        
        return sections
    
    def _extract_keywords(self, content_lines: List[str]) -> List[str]:
        """从内容中提取关键词"""
        # 操作系统文件管理相关的关键词
        keywords_set = set()
        
        important_terms = [
            "文件", "文件系统", "目录", "inode", "FCB", "文件控制块",
            "连续分配", "链接分配", "索引分配", "多级索引",
            "空闲表", "空闲链表", "位示图", "成组链接",
            "硬链接", "软链接", "符号链", "路径", "绝对路径", "相对路径",
            "权限", "访问控制", "ACL", "rwx", "共享", "保护", "加密",
            "创建", "删除", "打开", "关闭", "读", "写", "seek",
            "备份", "恢复", "快照", "日志", "RAID",
            "流式文件", "记录式文件", "逻辑结构", "物理结构",
            "单级目录", "两级目录", "树形目录", "哈希检索",
            "FAT", "ext", "Unix", "Linux"
        ]
        
        text = " ".join(content_lines).lower()
        
        for term in important_terms:
            if term.lower() in text:
                keywords_set.add(term)
        
        return list(keywords_set)
    
    def _build_index(self):
        """构建倒排索引"""
        self.index = {}
        
        for i, doc in enumerate(self.documents):
            # 基于关键词建立索引
            for keyword in doc["keywords"]:
                if keyword not in self.index:
                    self.index[keyword] = []
                self.index[keyword].append(i)
            
            # 基于标题建立索引
            title_words = doc["section_title"].lower().split()
            for word in title_words:
                if len(word) > 1:
                    if word not in self.index:
                        self.index[word] = []
                    self.index[word].append(i)
    
    def _calculate_relevance(self, query: str, doc: Dict) -> float:
        """计算查询与文档的相关性分数"""
        score = 0.0
        query_lower = query.lower()
        
        # 关键词匹配
        for keyword in doc["keywords"]:
            if keyword.lower() in query_lower:
                score += 2.0
        
        # 标题匹配
        title_lower = doc["section_title"].lower()
        query_words = query_lower.split()
        
        for word in query_words:
            if len(word) > 2 and word in title_lower:
                score += 3.0
        
        # 内容匹配
        content_lower = doc["content"].lower()
        for word in query_words:
            if len(word) > 2 and word in content_lower:
                score += 0.5
        
        # 章节相关性加权
        chapter_keywords = {
            "01": ["文件", "文件系统", "属性", "层次"],
            "02": ["结构", "分配", "索引", "连续", "链接"],
            "03": ["目录", "FCB", "inode", "路径", "树形"],
            "04": ["空闲", "位示图", "链表", "存储"],
            "05": ["共享", "保护", "权限", "加密", "链接"],
            "06": ["操作", "创建", "删除", "备份", "恢复"]
        }
        
        for ch_id, ch_keywords in chapter_keywords.items():
            if doc["chapter_id"] == ch_id:
                for kw in ch_keywords:
                    if kw in query_lower:
                        score += 1.5
        
        return score
    
    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        查询知识库并生成回答
        
        Args:
            question: 用户问题
            top_k: 返回最相关的片段数量
            
        Returns:
            包含回答、来源和置信度的字典
        """
        if not self.documents:
            return {
                "answer": "知识库中暂无相关内容，请咨询老师",
                "sources": [],
                "confidence": 0.0
            }
        
        # 计算所有文档的相关性分数
        scored_docs = []
        for i, doc in enumerate(self.documents):
            score = self._calculate_relevance(question, doc)
            if score > 0:
                scored_docs.append((score, doc))
        
        # 按分数排序
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # 获取 top_k 个最相关的文档
        top_docs = scored_docs[:top_k]
        
        if not top_docs:
            return {
                "answer": "知识库中暂无相关内容，请咨询老师",
                "sources": [],
                "confidence": 0.0
            }
        
        # 生成回答
        answer = self._generate_answer(question, top_docs)
        
        # 准备来源信息
        sources = []
        for score, doc in top_docs:
            sources.append({
                "chapter": f"第{self._chapter_num(doc['chapter_id'])}章 {doc['chapter_title']}",
                "section": doc["section_title"],
                "relevance": round(score, 2)
            })
        
        # 计算置信度
        confidence = min(1.0, top_docs[0][0] / 10.0) if top_docs else 0.0
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": round(confidence, 2)
        }
    
    def _chapter_num(self, chapter_id: str) -> str:
        """将章节 ID 转换为中文数字"""
        mapping = {
            "01": "一", "02": "二", "03": "三",
            "04": "四", "05": "五", "06": "六"
        }
        return mapping.get(chapter_id, chapter_id)
    
    def _generate_answer(self, question: str, docs: List[tuple]) -> str:
        """基于检索到的文档生成回答"""
        if not docs:
            return "知识库中暂无相关内容，请咨询老师"
        
        # 收集相关信息
        relevant_info = []
        for score, doc in docs:
            info = f"【{doc['section_title']}】\n{doc['content'][:500]}"
            if len(doc["content"]) > 500:
                info += "..."
            relevant_info.append(info)
        
        # 构建回答
        answer_parts = []
        
        # 开头
        answer_parts.append("根据文件管理章节的知识库内容，为您解答：\n")
        
        # 主体内容
        for i, info in enumerate(relevant_info, 1):
            answer_parts.append(f"{i}. {info}\n")
        
        # 结尾提示
        answer_parts.append("\n💡 如需了解更多细节，请查阅教材对应章节或咨询老师。")
        
        return "\n".join(answer_parts)
    
    def get_chapter_content(self, chapter_id: str) -> str:
        """获取指定章节的全部内容"""
        chapter_docs = [
            doc for doc in self.documents 
            if doc["chapter_id"] == chapter_id
        ]
        
        if not chapter_docs:
            return "该章节内容暂无"
        
        contents = []
        for doc in chapter_docs:
            contents.append(f"## {doc['section_title']}\n\n{doc['content']}")
        
        return "\n\n".join(contents)
