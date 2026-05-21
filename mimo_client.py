"""MiMo API 客户端 — 兼容 OpenAI Chat Completions 格式"""

from openai import OpenAI
from config import MIMO_API_BASE, MIMO_API_KEY, MIMO_CHAT_MODEL


class MiMoClient:
    """封装 MiMo 模型调用的客户端"""

    def __init__(self, api_key=None, api_base=None, model=None):
        self.api_key = api_key or MIMO_API_KEY
        self.api_base = api_base or MIMO_API_BASE
        self.model = model or MIMO_CHAT_MODEL

        if not self.api_key:
            raise ValueError("API Key 未设置，请在界面左侧输入")

        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)

    def chat(self, messages, temperature=0.7, max_tokens=4096):
        """基础对话方法"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def chat_with_context(self, system_prompt, user_query, context_chunks, chat_history=None):
        """带 RAG 上下文增强的对话"""
        context = "\n\n".join(
            f"[文献片段 {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)
        )

        messages = [{"role": "system", "content": system_prompt}]

        # 附带最近对话历史（最多 6 轮）
        if chat_history:
            messages.extend(chat_history[-6:])

        messages.append({
            "role": "user",
            "content": (
                f"以下是相关文献内容：\n\n{context}\n\n"
                f"请严格基于以上文献内容回答以下问题：\n{user_query}"
            ),
        })

        return self.chat(messages)
