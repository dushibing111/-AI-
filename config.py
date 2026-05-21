"""PaperAI 配置 — 所有可调整参数集中管理"""

import os

# ── MiMo API ──
MIMO_API_BASE = os.getenv("MIMO_API_BASE", "https://api.360.cn/v1")
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
MIMO_CHAT_MODEL = os.getenv("MIMO_CHAT_MODEL", "xiaomi/mimo-v2.5")

# ── RAG 参数 ──
CHUNK_SIZE = 800          # 每个文本片段的词数
CHUNK_OVERLAP = 150       # 相邻片段重叠词数
TOP_K_RESULTS = 5          # 检索返回的最相关片段数

# ── Embedding ──
# 使用本地 sentence-transformers 模型生成向量（无需 API 调用）
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── 应用 ──
APP_TITLE = "PaperAI — 论文智能分析助手"
APP_ICON = "📄"
