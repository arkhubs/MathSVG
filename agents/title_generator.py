# agents/title_generator.py
from langchain_core.messages import HumanMessage, SystemMessage
from config import text_llm
from prompts import TITLE_GENERATOR_PROMPT
import re

def get_title_from_description(structured_description: str) -> str:
    """
    根据结构化的几何描述生成一个适合文件系统的双语标题。
    """
    print("-> Calling Title Generator...")
    system_message = SystemMessage(content=TITLE_GENERATOR_PROMPT)
    human_message = HumanMessage(content=structured_description)

    response = text_llm.invoke([system_message, human_message])
    title = response.content.strip()

    # 移除不适合用作文件名的特殊字符
    # 允许下划线、连字符和中文字符
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    # 将空格替换为下划线
    title = re.sub(r'\s+', '_', title)
    
    print(f"--- Generated Title: {title} ---")
    return title
