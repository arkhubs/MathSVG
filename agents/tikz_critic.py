# agents/tikz_critic.py
from langchain_core.messages import HumanMessage, SystemMessage
from config import text_llm
from prompts import CRITIC_PROMPT_TIKZ

def get_tikz_critic_response(structured_description: str, latex_code: str, compilation_result: dict) -> str:
    """
    调用审查员LLM来审查LaTeX代码和编译结果。
    """
    print("-> Calling Critic...")
    system_message = SystemMessage(content=CRITIC_PROMPT_TIKZ)
    
    # 将所有信息组合成一个清晰的上下文
    compilation_status = "Success" if compilation_result["success"] else f"Failure:\n{compilation_result['error']}"
    
    review_content = f"""
    **1. Original Geometric Description (JSON):**
    ```json
    {structured_description}
    ```

    **2. Generated LaTeX Code:**
    ```latex
    {latex_code}
    ```
    
    **3. Compilation Result:**
    {compilation_status}
    """
    human_message = HumanMessage(content=review_content)

    response = text_llm.invoke([system_message, human_message])
    return response.content.strip()
