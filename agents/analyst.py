# agents/analyst.py
from langchain_core.messages import HumanMessage, SystemMessage
from config import multimodal_llm
from prompts import ANALYST_PROMPT_ENHANCED  # 使用新的 Prompt
from tools.pdf_utils import pdf_to_base64_images
import base64
import os

def get_analyst_response(user_request: dict) -> str:
    """
    调用几何分析师LLM。
    可以处理初始请求，也可以处理包含反馈的诊断任务。
    """
    print("-> Calling Geometric Analyst...")
    system_message = SystemMessage(content=ANALYST_PROMPT_ENHANCED)
    
    content = []
    
    # 场景一：初始请求
    if user_request["type"] == "initial_text":
        content.append({"type": "text", "text": f"这是用户的初始请求，请执行职责一进行分析：\n\n{user_request['data']}"})

    elif user_request["type"] == "initial_image":
        image_path = user_request["data"]
        try:
            with open(image_path, "rb") as image_file:
                b64_image = base64.b64encode(image_file.read()).decode('utf-8')
            content.append({"type": "text", "text": "这是用户的手绘草图，请执行职责一进行分析，将其转换为结构化的JSON格式。"})
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}})
        except Exception as e:
            return f"Error reading image file: {e}"

    # 场景二：诊断与修正
    elif user_request["type"] == "feedback":
        feedback_data = user_request["data"]
        text_prompt = f"""
        请执行职责二进行诊断和修正。以下是反馈包：

        1.  **你上次生成的JSON描述 (规划)**:
            ```json
            {feedback_data['original_description']}
            ```
        
        2.  **审查员的意见**:
            {feedback_data['critic_feedback']}

        3.  **编译日志 (截取)**:
            ```
            {feedback_data['log_content']}
            ```
        
        请结合下面的PDF截图，分析问题并决定是修正JSON还是维持原样。
        """
        content.append({"type": "text", "text": text_prompt})

        # 将PDF转换为图片并添加到content中
        b64_images = pdf_to_base64_images(feedback_data['pdf_path'])
        if b64_images:
            for b64_image in b64_images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_image}"}
                })
        else:
             content.append({"type": "text", "text": "\n(无法加载PDF截图。请仅根据文本信息进行诊断。)"})

    else:
        return "Error: Invalid request type."

    human_message = HumanMessage(content=content)
    response = multimodal_llm.invoke([system_message, human_message])
    return response.content
