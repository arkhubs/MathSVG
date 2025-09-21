# tools/logger.py
import datetime
import os

def get_timestamp():
    """返回标准格式的当前时间戳。"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def initialize_log(directory: str) -> str:
    """
    在指定的目录中初始化一个日志文件。
    返回日志文件的完整路径。
    """
    log_path = os.path.join(directory, "workflow_log.txt")
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"[{get_timestamp()}] --- 工作流日志初始化 ---\n")
            f.write(f"日志文件创建于: {log_path}\n")
        return log_path
    except Exception as e:
        # 在主程序中打印错误，因为日志本身可能无法工作
        print(f"错误：无法初始化日志文件于 {log_path}: {e}")
        return ""

def log_message(log_path: str, message: str, title: str = ""):
    """
    将一条格式化的消息追加到指定的日志文件中。
    """
    if not log_path:
        return
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*70 + "\n")
            if title:
                f.write(f"[{get_timestamp()}] --- {title.upper()} ---\n\n")
            else:
                f.write(f"[{get_timestamp()}]\n\n")
            f.write(message.strip() + "\n")
            f.write("="*70 + "\n")
    except Exception as e:
        print(f"错误：无法写入日志文件 {log_path}: {e}")
