# main.py
import os

from workflow import build_workflow
from tools.logger import log_message # 新增导入

def main():
    """主函数，运行整个智能体系统"""
    app = build_workflow()

    print("\n--- Welcome to the Geometric Vectorization Agent System ---")
    print("You can provide a text description or a path to an image file (e.g., sketch.png).")
    user_input = input("> ")

    initial_request = {}
    # 判断输入是文件路径还是文本描述
    if os.path.exists(user_input):
        initial_request = {"type": "image", "data": user_input}  # 保持向后兼容
        print(f"Processing image file: {user_input}")
    else:
        initial_request = {"type": "text", "data": user_input}  # 保持向后兼容
        print(f"Processing text description: '{user_input}'")

    # 定义初始状态
    initial_state = {"initial_request": initial_request}

    # 流式执行工作流并打印每一步的结果
    final_state = None
    for event in app.stream(initial_state):
        # event 是一个字典，key是节点名，value是该节点的输出
        (node_name, node_output), = event.items()
        print(f"\n<<< Finished Node: {node_name} >>>")
        # print(f"Output: {node_output}")
        
        # 更新最终状态，保持状态累积
        if final_state:
            final_state.update(node_output)
        else:
            final_state = node_output

    print("\n--- Workflow Finished ---")
    
    # 提取并展示最终结果

    if final_state:
        # 新增: 获取日志文件路径
        log_path = final_state.get("log_file_path", "")
        final_summary_log = [] # 用于存储日志信息的列表

        saved_files = final_state.get("saved_files", [])
        if saved_files:
            msg = "\n✅ The following PDF files were successfully generated during the process:"
            print(msg)
            final_summary_log.append(msg)
            for file_path in saved_files:
                print(f"- {file_path}")
                final_summary_log.append(f"- {file_path}")

        if final_state.get("critic_feedback") == "APPROVED":
            msg = "\n✅ Success! The process was approved on the final attempt."
            print(msg)
            final_summary_log.append(msg)
            latest_pdf = saved_files[-1] if saved_files else "No file"
            msg = f"Final approved file: {latest_pdf}"
            print(msg)
            final_summary_log.append(msg)
        else:
            msg = "\n❌ Failure. The process finished without final approval."
            print(msg)
            final_summary_log.append(msg)
            feedback = final_state.get('critic_feedback', 'No final feedback.')
            msg = f"Final Feedback from Critic:\n{feedback}"
            print(msg)
            final_summary_log.append(msg)
            code = final_state.get('latex_code', 'No final code generated.')
            msg = f"\nLast Generated LaTeX Code:\n{code}"
            print(msg)
            final_summary_log.append(msg)

        # 新增: 将最终总结写入日志并告知用户
        if log_path:
            log_message(log_path, "\n".join(final_summary_log), title="最终总结")
            print(f"\n📄 A detailed log of this workflow has been saved to: {log_path}")

    else:
        print("An unexpected error occurred and the workflow did not complete.")


if __name__ == "__main__":
    main()
