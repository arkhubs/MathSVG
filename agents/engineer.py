# agents/engineer.py
from langchain_core.messages import HumanMessage, SystemMessage
from config import text_llm
from prompts import ENGINEER_PROMPT
from tools.python_executor import execute_python_code
import re # 导入正则表达式库

def parse_python_code(llm_response: str) -> str:
    """
    从LLM的响应中提取Python代码块。
    """
    # 使用正则表达式查找被 ```python ... ``` 包围的代码
    match = re.search(r"```python\n(.*?)\n```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    # 如果没有找到代码块，就假设整个响应都是代码（作为备用方案）
    return llm_response.strip()

def get_engineer_response(structured_description: str, output_filename: str) -> dict:
    """
    调用SVG工程师LLM生成Python代码，并执行它。
    现在会将 structured_description 注入到 prompt 中。
    """
    print("-> Calling SVG Engineer...")
    
    # 关键步骤：将分析师的JSON输出注入到Prompt模板中
    prompt = ENGINEER_PROMPT.format(
        output_filename=output_filename,
        json_data_placeholder=structured_description
    )
    
    system_message = SystemMessage(content=prompt)
    # HumanMessage 现在可以为空，或者提供一个简单的启动指令
    human_message = HumanMessage(content="Please complete the Python script based on the provided template and JSON data.")

    # 生成代码
    code_response = text_llm.invoke([system_message, human_message])
    full_response = code_response.content
    
    # 关键步骤：解析出纯净的代码
    python_code = parse_python_code(full_response)

    print("\n--- Generated Python Code (Cleaned) ---")
    print(python_code)
    print("----------------------------------------\n")

    # 执行代码，传入动态的文件名
    execution_result = execute_python_code(python_code, output_filename)

    return {
        "python_code": python_code,
        "execution_result": execution_result,
        "output_filename": output_filename # 将文件名也返回
    }
