# config.py
import os
import yaml
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（如果存在）
load_dotenv()

def load_config(config_path="config.yaml"):
    """从 YAML 文件和环境变量加载配置"""
    # 从 YAML 文件加载默认配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 优先使用环境变量覆盖配置
    api_key = os.getenv("CUSTOM_API_KEY", config.get("api_key"))
    base_url = os.getenv("CUSTOM_BASE_URL", config.get("base_url"))
    multimodal_model_name = os.getenv("CUSTOM_MODEL_NAME", config.get("multimodal_model"))
    text_model_name = os.getenv("CUSTOM_TEXT_MODEL_NAME", config.get("text_model"))

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise ValueError("API key not found. Please set it in config.yaml or as CUSTOM_API_KEY environment variable.")

    return {
        "api_key": api_key,
        "base_url": base_url,
        "multimodal_model_name": multimodal_model_name,
        "text_model_name": text_model_name,
    }

# 加载配置
APP_CONFIG = load_config()

# 初始化 LLM 实例，以便在整个项目中重复使用
# 多模态模型
multimodal_llm = ChatOpenAI(
    model=APP_CONFIG["multimodal_model_name"],
    api_key=APP_CONFIG["api_key"],
    base_url=APP_CONFIG["base_url"],
    temperature=0.1,
    max_tokens=4096,
    request_timeout=60  # <-- 增加超时设置 (60秒)
)

# 文本模型
text_llm = ChatOpenAI(
    model=APP_CONFIG["text_model_name"],
    api_key=APP_CONFIG["api_key"],
    base_url=APP_CONFIG["base_url"],
    temperature=0.0, # 对于代码生成和审查，需要确定性
    max_tokens=4096,
    request_timeout=60  # <-- 增加超时设置 (60秒)
)

print("✅ Configuration loaded successfully.")
print(f"✅ Multimodal Model: {APP_CONFIG['multimodal_model_name']}")
print(f"✅ Text Model: {APP_CONFIG['text_model_name']}")
