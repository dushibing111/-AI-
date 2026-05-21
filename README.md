# 📄 PaperAI — 论文智能分析助手

> 基于 **Claude (Claude Code)** 辅助开发 + RAG（检索增强生成）的学术论文分析工具。  
> 上传 PDF 论文，即可进行深度问答、摘要生成、创新点挖掘等操作。

---

## ✨ 功能亮点

| 功能 | 说明 |
|------|------|
| 📁 **PDF 自动解析** | 上传论文 PDF，自动提取全文内容 |
| 🧠 **RAG 智能检索** | 语义分块 + FAISS 向量检索，准确找到相关内容 |
| 💬 **深度问答** | 基于大模型（可接入 MiMo/Claude/OpenAI），结合论文内容回答问题 |
| 📋 **一键摘要** | 自动生成论文核心摘要 |
| 🏷️ **关键信息提取** | 提取研究目的、方法、数据集、实验结果等 |
| 🎯 **创新点分析** | 自动识别论文的核心创新点 |

## 🏗️ 技术架构

```
用户提问 → 语义检索(FAISS) → 相关文本片段
                                    ↓
用户 ← LLM 回答 ← 拼接 Prompt + 上下文
```

- **前端/UI**：Streamlit
- **PDF 解析**：PyMuPDF (fitz)
- **向量检索**：sentence-transformers + FAISS（本地运行，无需额外 API）
- **大模型**：兼容 OpenAI 格式的任意模型（MiMo / Claude / OpenAI）
- **辅助开发**：Claude Code（Claude Opus 4.7）
- **语言**：Python 3.10+

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

> 首次运行时会自动下载 embedding 模型（`all-MiniLM-L6-v2`，约 80MB），只需几秒钟。

### 2. 启动应用

```bash
streamlit run app.py
```

### 3. 配置 API Key（以 MiMo 为例）

在界面左侧填入你的 API Key（通过 [100t.xiaomimimo.com](https://100t.xiaomimimo.com) 申请 MiMo 免费额度）：

| 参数 | 默认值 |
|------|--------|
| API 地址 | `https://api.360.cn/v1` |
| 模型名称 | `xiaomi/mimo-v2.5` |

> 也可接入 Claude API 或其他兼容 OpenAI 格式的模型。

### 4. 上传论文

- 支持任意学术 PDF
- 自动分块并建立索引
- 完成后即可开始对话

### 5. 开始提问

示例问题：
- "这篇论文主要研究了什么？"
- "采用了什么研究方法？"
- "主要实验结论是什么？"
- "论文的创新点有哪些？"

---

## 📁 项目结构

```
paper-ai-assistant/
├── app.py            # Streamlit 主入口（UI + 交互逻辑）
├── paper_rag.py      # RAG 引擎（PDF 解析 → 分块 → FAISS 检索）
├── mimo_client.py    # MiMo API 客户端
├── config.py         # 集中配置
├── requirements.txt  # Python 依赖
└── .gitignore
```

## 🧪 运行截图

*(建议添加 2-3 张运行截图到这里，审核时会加分)*

## 📝 申请活动说明

本项目是为申请 **小米 MiMo Orbit 百万亿 Token 创造者激励计划** 而创建的 Demo。

**技术亮点**：
- ✅ 完整的 RAG 架构（检索增强生成）
- ✅ 本地向量检索（无需额外 API 费用）
- ✅ 使用 Claude Code 辅助开发，效率大幅提升
- ✅ 对学术场景有实用价值

---

## 📄 开源协议

MIT
