"""
RAG的共通模型
"""
from langchain_openai import ChatOpenAI
from src.config import settings

_response_model = ChatOpenAI(
    model=settings.openai_model,
    temperature=0
)