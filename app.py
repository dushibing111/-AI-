"""PaperAI — 论文智能分析助手（Streamlit 主入口）"""

import os
import tempfile

import streamlit as st

from config import APP_TITLE, APP_ICON
from mimo_client import MiMoClient
from paper_rag import PaperRAG

# ── 页面配置 ──
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown(
    "基于 **小米 MiMo-V2.5** 大模型的 RAG 论文分析工具。"
    "上传 PDF 后即可对论文进行深度问答、摘要生成、创新点挖掘等操作。"
)

# ── Session State ──
_DEFAULT = {
    "rag": PaperRAG(),
    "mimo": None,
    "messages": [],
    "pdf_ok": False,
}

for k, v in _DEFAULT.items():
    st.session_state.setdefault(k, v)

# ═══════════════════════════════════════════════════════════
#  侧边栏
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ API 配置")

    api_key = st.text_input("MiMo API Key", type="password",
                            help="兼容 OpenAI 格式的 MiMo API Key")
    api_base = st.text_input("API 地址",
                             value="https://api.360.cn/v1",
                             help="可通过 360 智脑 / OpenRouter 等渠道获取")
    model = st.text_input("模型名称", value="xiaomi/mimo-v2.5")

    if api_key:
        try:
            st.session_state.mimo = MiMoClient(api_key=api_key,
                                                api_base=api_base,
                                                model=model)
            st.success("✅ API 连接成功")
        except Exception as e:
            st.error(f"❌ {e}")

    st.divider()
    st.header("📁 论文上传")

    uploaded = st.file_uploader("选择 PDF 文件", type=["pdf"],
                                 label_visibility="collapsed")

    if uploaded and st.button("📄 处理论文", type="primary"):
        with st.spinner("解析 PDF → 文本分块 → 向量化索引…"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            try:
                meta = st.session_state.rag.process_pdf(tmp_path, uploaded.name)
                st.session_state.pdf_ok = True
                st.session_state.messages = []  # 新论文 → 清空聊天
                st.success(f"✅ 处理完成！")
                st.info(f"📊 {meta['total_chunks']} 个片段 | {meta['total_chars']:,} 字符")
            except Exception as e:
                st.error(f"❌ 处理失败: {str(e)}")
            finally:
                os.unlink(tmp_path)

    # ── 快速操作 ──
    if st.session_state.pdf_ok:
        st.divider()
        st.header("⚡ 快捷操作")
        if st.button("📋 生成论文摘要", use_container_width=True):
            st.session_state._quick = "请用 200 字以内概括这篇论文的核心内容，包括研究背景、方法、主要发现和结论。"
        if st.button("🏷️ 提取关键信息", use_container_width=True):
            st.session_state._quick = "请提取这篇论文的关键信息：研究目的、方法、数据集、实验结果、创新点、局限性。以 Markdown 列表呈现。"
        if st.button("🎯 核心创新点", use_container_width=True):
            st.session_state._quick = "这篇论文的主要创新点是什么？相比已有工作有哪些实质性突破？请具体说明。"

    # ── 使用指引 ──
    st.divider()
    with st.expander("💡 使用指引"):
        st.markdown("""
        1. 在 **API 配置** 区输入你的 MiMo API Key
        2. 上传一篇 **PDF 论文**
        3. 在聊天区提问，例如：
           - "这篇论文用了什么方法？"
           - "实验设置是怎样的？"
           - "主要结论是什么？"
        4. 也可使用右侧的 **快捷操作**
        """)

# ═══════════════════════════════════════════════════════════
#  主区域 — 聊天
# ═══════════════════════════════════════════════════════════

col_chat, col_info = st.columns([3, 1])

with col_chat:
    # 处理快捷操作
    if q := st.session_state.pop("_quick", None):
        st.session_state.messages.append({"role": "user", "content": q})
        # 标记自动发送
        st.session_state._auto_send = True

    # 聊天记录
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 自动回答（快捷操作触发的请求）
    if st.session_state.pop("_auto_send", False):
        last = st.session_state.messages[-1]
        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("分析中…"):
                results = st.session_state.rag.search(last["content"])
                chunks = [r["content"] for r in results]

                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[-10:-1]
                ]

                SYSTEM_PROMPT = """你是一个专业的论文分析助手。请严格遵守以下准则：
1. 只基于提供的文献内容回答，不编造、不臆测
2. 如果文献中没有相关信息，明确告知用户
3. 必要时引用原文片段（标注「文献片段 X」）
4. 使用结构化、清晰的格式回答
5. 始终使用中文"""

                try:
                    resp = st.session_state.mimo.chat_with_context(
                        system_prompt=SYSTEM_PROMPT,
                        user_query=last["content"],
                        context_chunks=chunks,
                        chat_history=history,
                    )
                    placeholder.markdown(resp)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": resp}
                    )
                except Exception as e:
                    placeholder.error(f"调用 MiMo API 失败: {e}")

    # ── 输入框 ──
    disabled = not (st.session_state.pdf_ok and st.session_state.mimo)
    placeholder_txt = (
        "请先在左侧上传论文并配置 API…" if not st.session_state.pdf_ok
        else "请先在左侧配置 MiMo API Key…" if not st.session_state.mimo
        else "输入关于论文的问题…"
    )

    if prompt := st.chat_input(placeholder_txt, disabled=disabled):
        # 用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 助手回答
        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("正在检索并分析论文…"):
                results = st.session_state.rag.search(prompt)
                chunks = [r["content"] for r in results]

                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[-10:-1]
                ]

                SYSTEM_PROMPT = """你是一个专业的论文分析助手。请严格遵守以下准则：
1. 只基于提供的文献内容回答，不编造、不臆测
2. 如果文献中没有相关信息，明确告知用户
3. 必要时引用原文片段（标注「文献片段 X」）
4. 使用结构化、清晰的格式回答
5. 始终使用中文"""

                try:
                    resp = st.session_state.mimo.chat_with_context(
                        system_prompt=SYSTEM_PROMPT,
                        user_query=prompt,
                        context_chunks=chunks,
                        chat_history=history,
                    )
                    placeholder.markdown(resp)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": resp}
                    )
                except Exception as e:
                    placeholder.error(f"调用 MiMo API 失败: {e}")

# ── 右侧信息面板 ──
with col_info:
    if st.session_state.pdf_ok:
        meta = st.session_state.rag.metadata
        st.markdown(f"""
        **📄 当前论文**
        - 文件名：{meta['filename']}
        - 片段数：{meta['total_chunks']}
        - 字符数：{meta['total_chars']:,}
        """)

        st.divider()
        st.markdown("**💬 推荐问题**")
        suggestions = [
            "这篇论文研究的是什么问题？",
            "用了什么方法/模型？",
            "实验效果如何？",
            "有哪些局限性？",
            "未来工作方向是什么？",
        ]
        for sq in suggestions:
            if st.button(sq, use_container_width=True, key=f"sug_{sq[:6]}"):
                st.session_state.messages.append({"role": "user", "content": sq})
                st.session_state._auto_send = True
                st.rerun()
    else:
        st.info("📄 上传论文后将在此显示文档概览")
