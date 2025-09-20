# agents/critic.py
from langchain_core.messages import HumanMessage, SystemMessage
from config import text_llm
from prompts import CRITIC_PROMPT

def get_critic_response(structured_description: str, python_code: str) -> str:
    """
    调用审查员LLM来审查代码和描述。
    """
    print("-> Calling Critic...")
    system_message = SystemMessage(content=CRITIC_PROMPT)

    review_content = f"""
    Please review the following materials.

    **1. Geometric Description (JSON):**
    ```json
    {structured_description}
    ```

    **2. Generated Python Code:**
    ```python
    {python_code}
    ```
    """
    human_message = HumanMessage(content=review_content)

    response = text_llm.invoke([system_message, human_message])
    feedback = response.content.strip()

    print(f"--- Critic's Feedback ---\n{feedback}\n------------------------")

    return feedback
