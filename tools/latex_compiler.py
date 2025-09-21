# tools/latex_compiler.py
import os
import subprocess
import platform

# 修改 compile_latex_code 函数签名和逻辑

def compile_latex_code(latex_code: str, output_filename_base: str, output_dir: str) -> dict:
    """
    将 LaTeX 代码字符串写入 .tex 文件并使用 pdflatex 进行编译。
    此版本通过在目标目录中执行命令来增强路径处理的稳定性。
    """
    # 完整的文件路径
    tex_filepath = f"{output_filename_base}.tex"
    pdf_filepath = f"{output_filename_base}.pdf"
    log_filepath = f"{output_filename_base}.log"

    # 从完整路径中仅提取文件名
    tex_filename_only = os.path.basename(tex_filepath)

    try:
        # 目录创建已在工作流中完成，此处为安全校验
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 将 .tex 文件写入目标子目录
        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(latex_code)

        # 构建 pdflatex 命令，现在只使用文件名，因为我们将在该目录中运行
        command = [
            "pdflatex",
            "-interaction=nonstopmode",
            tex_filename_only  # 只传递文件名
        ]

        # 在 Windows 上隐藏命令行窗口
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # 【核心修正】: 使用 cwd 参数指定命令的执行目录
        process = subprocess.run(
            command,
            cwd=output_dir,  # 在目标输出目录中执行命令
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )

        # 检查PDF文件是否在预期位置生成
        if process.returncode == 0 and os.path.exists(pdf_filepath):
            return {"success": True, "path": pdf_filepath, "log": f"Compilation successful. Log file at {log_filepath}"}
        else:
            # 尝试读取日志文件获取更详细的错误
            error_log = ""
            if os.path.exists(log_filepath):
                with open(log_filepath, 'r', encoding='utf-8', errors='replace') as log_file:
                    log_content = log_file.read()
                    errors = [line for line in log_content.splitlines() if line.startswith("!")]
                    error_log = "\n".join(errors) if errors else log_content[-1000:]

            error_message = f"pdflatex compilation failed with return code {process.returncode}.\n"
            error_message += f"Executed in: {output_dir}\n"
            error_message += f"STDOUT:\n{process.stdout}\n"
            error_message += f"STDERR:\n{process.stderr}\n"
            error_message += f"ERROR LOG:\n{error_log}"
            return {"success": False, "error": error_message}

    except FileNotFoundError:
        error = "Error: 'pdflatex' command not found. Please ensure a LaTeX distribution (like MiKTeX or TeX Live) is installed and in your system's PATH."
        return {"success": False, "error": error}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}
