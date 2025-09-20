# tools/python_executor.py
import os
from contextlib import redirect_stdout
from io import StringIO
import traceback

def execute_python_code(python_code: str, output_filename: str) -> dict:
    """
    安全地执行一段Python代码，并返回一个结构化的字典结果。
    """
    try:
        if not os.path.exists("outputs"):
            os.makedirs("outputs")

        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            exec(python_code, {})

        output = output_buffer.getvalue()

        if os.path.exists(output_filename):
            return {"success": True, "path": output_filename, "output": output}
        else:
            error_msg = f"Code executed without raising an exception, but the output file '{output_filename}' was not created."
            return {"success": False, "error": error_msg, "output": output}

    except Exception as e:
        error_trace = traceback.format_exc()
        return {"success": False, "error": error_trace, "output": ""}
