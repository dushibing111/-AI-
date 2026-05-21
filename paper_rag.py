"""RAG 引擎 — PDF 解析、文本分块、向量检索"""

import os
import tempfile

import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS, EMBEDDING_MODEL


class PaperRAG:
    """论文 RAG 引擎：PDF → 分块 → Embedding → FAISS 检索"""

    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.chunks: list[str] = []
        self.metadata: dict = {}

    # ── PDF 解析 ──

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """用 PyMuPDF 提取 PDF 全文"""
        doc = fitz.open(pdf_path)
        pages = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                pages.append(f"--- 第 {page_num + 1} 页 ---\n{text}")
        doc.close()
        return "\n".join(pages)

    # ── 文本分块 ──

    def chunk_text(self, text: str) -> list[str]:
        """按词数 + 重叠分块"""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + CHUNK_SIZE, len(words))
            chunks.append(" ".join(words[start:end]))
            start += CHUNK_SIZE - CHUNK_OVERLAP
            if end == len(words):
                break  # 已处理完最后一块
        return chunks

    # ── 全文处理流水线 ──

    def process_pdf(self, pdf_path: str, filename: str) -> dict:
        """完整流水线：提取 → 分块 → 向量化 → 建索引"""
        text = self.extract_text_from_pdf(pdf_path)
        self.chunks = self.chunk_text(text)
        self.metadata = {
            "filename": filename,
            "total_chunks": len(self.chunks),
            "total_chars": len(text),
        }

        # 生成向量 + FAISS 索引
        embeddings = self.embedder.encode(self.chunks, show_progress_bar=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype("float32"))

        return self.metadata

    # ── 语义检索 ──

    def search(self, query: str, k: int | None = None) -> list[dict]:
        """检索与 query 语义最相关的 k 个文本片段"""
        if self.index is None or not self.chunks:
            return []
        k = k or TOP_K_RESULTS
        q_vec = self.embedder.encode([query]).astype("float32")
        distances, indices = self.index.search(q_vec, k)

        results = []
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(self.chunks):
                results.append({
                    "content": self.chunks[idx],
                    "score": float(distances[0][i]),
                })
        return results
