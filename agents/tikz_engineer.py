# agents/tikz_engineer.py
from langchain_core.messages import HumanMessage, SystemMessage
from config import text_llm
from prompts import TIKZ_ENGINEER_PROMPT

def get_tikz_engineer_response(structured_description: str) -> str:
    """
    调用 TikZ 工程师 LLM 生成 LaTeX 代码。
    """
    print("-> Calling TikZ Engineer...")
    system_message = SystemMessage(content=TIKZ_ENGINEER_PROMPT)
    human_message = HumanMessage(content=structured_description)
    
    response = text_llm.invoke([system_message, human_message])
    # TikZ/LaTeX 代码不需要解析，直接返回内容
    return response.content.strip()
