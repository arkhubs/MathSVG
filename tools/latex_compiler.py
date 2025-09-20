# tools/latex_compiler.py
import os
import subprocess
import platform

def compile_latex_code(latex_code: str, output_filename_base: str) -> dict:
    """
    将 LaTeX 代码字符串写入 .tex 文件并使用 pdflatex 进行编译。
    output_filename_base 是不带扩展名的文件名，例如 "outputs/geometry_v1"
    """
    tex_filepath = f"{output_filename_base}.tex"
    pdf_filepath = f"{output_filename_base}.pdf"
    log_filepath = f"{output_filename_base}.log"

    try:
        if not os.path.exists("outputs"):
            os.makedirs("outputs")

        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(latex_code)

        # 构建 pdflatex 命令
        # -interaction=nonstopmode: 遇到错误时不暂停，继续执行
        # -output-directory=outputs: 指定输出目录
        command = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory=outputs",
            tex_filepath
        ]

        # 在 Windows 上，可能需要隐藏命令行窗口
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # 执行编译命令
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )

        if process.returncode == 0 and os.path.exists(pdf_filepath):
            return {"success": True, "path": pdf_filepath, "log": f"Compilation successful. Log file at {log_filepath}"}
        else:
            # 尝试读取日志文件获取更详细的错误
            error_log = ""
            if os.path.exists(log_filepath):
                with open(log_filepath, 'r', encoding='utf-8', errors='replace') as log_file:
                    log_content = log_file.read()
                    # 查找 LaTeX 错误信息（通常以 "!" 开头）
                    errors = [line for line in log_content.splitlines() if line.startswith("!")]
                    error_log = "\n".join(errors) if errors else log_content[-1000:] # 如果找不到特定错误，显示日志末尾

            error_message = f"pdflatex compilation failed with return code {process.returncode}.\n"
            error_message += f"STDOUT:\n{process.stdout}\n"
            error_message += f"STDERR:\n{process.stderr}\n"
            error_message += f"ERROR LOG:\n{error_log}"
            return {"success": False, "error": error_message}

    except FileNotFoundError:
        error = "Error: 'pdflatex' command not found. Please ensure a LaTeX distribution (like TeX Live) is installed and in your system's PATH."
        return {"success": False, "error": error}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}
