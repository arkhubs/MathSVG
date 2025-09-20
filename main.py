# main.py
import os
from workflow import build_workflow

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
        saved_files = final_state.get("saved_files", [])
        if saved_files:
            print("\n✅ The following PDF files were successfully generated during the process:")
            for file_path in saved_files:
                print(f"- {file_path}")

        if final_state.get("critic_feedback") == "APPROVED":
            print("\n✅ Success! The process was approved on the final attempt.")
            latest_pdf = saved_files[-1] if saved_files else "No file"
            print(f"Final approved file: {latest_pdf}")
        else:
            print("\n❌ Failure. The process finished without final approval.")
            feedback = final_state.get('critic_feedback', 'No final feedback.')
            print(f"Final Feedback from Critic:\n{feedback}")
            # 最后一个生成的代码，无论成功与否
            code = final_state.get('latex_code', 'No final code generated.')
            print(f"\nLast Generated LaTeX Code:\n{code}")
    else:
        print("An unexpected error occurred and the workflow did not complete.")


if __name__ == "__main__":
    main()
