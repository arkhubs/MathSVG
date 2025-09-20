# workflow.py
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import json
import os

from agents.analyst import get_analyst_response
from agents.tikz_engineer import get_tikz_engineer_response
from agents.tikz_critic import get_tikz_critic_response
from tools.latex_compiler import compile_latex_code

MAX_ITERATIONS = 5

class AgentState(TypedDict):
    """定义工作流的状态"""
    initial_request: dict
    structured_description: str
    latex_code: str
    compilation_result: Dict[str, Any]
    critic_feedback: str
    iteration_count: int
    saved_files: List[str]
    # 新增字段，用于在反馈循环中传递文件路径
    last_pdf_path: str
    last_log_path: str

# --- 节点定义 ---

def initial_analyst_node(state: AgentState) -> AgentState:
    """仅用于处理初始请求的分析师节点"""
    print("--- NODE: INITIAL ANALYST ---")
    request = state["initial_request"]
    # 区分请求类型
    if os.path.exists(request['data']):
         req = {"type": "initial_image", "data": request['data']}
    else:
         req = {"type": "initial_text", "data": request['data']}

    description = get_analyst_response(req)
    return {"structured_description": description, "iteration_count": 0, "saved_files": []}

def triage_analyst_node(state: AgentState) -> AgentState:
    """处理反馈、进行诊断和修正的分析师节点"""
    print("--- NODE: TRIAGE ANALYST ---")
    
    log_content = ""
    try:
        with open(state['last_log_path'], 'r', encoding='utf-8', errors='replace') as f:
            log_content = f.read()[-1500:] # 只读取日志的最后部分
    except Exception:
        log_content = "Log file not found or could not be read."

    feedback_package = {
        "type": "feedback",
        "data": {
            "original_description": state["structured_description"],
            "critic_feedback": state["critic_feedback"],
            "pdf_path": state["last_pdf_path"],
            "log_content": log_content
        }
    }
    
    # 调用分析师进行诊断，并获取可能被修正后的新JSON
    new_description = get_analyst_response(feedback_package)
    print("\n--- Analyst Triage Result (New Description) ---")
    print(new_description)
    print("-----------------------------------------------\n")

    # 更新状态中的几何描述
    return {"structured_description": new_description}

def engineer_node(state: AgentState) -> AgentState:
    """TikZ工程师节点"""
    print("--- NODE: TIKZ ENGINEER & COMPILER ---")
    description = state["structured_description"]
    current_iteration = state["iteration_count"]
    
    feedback = state.get("critic_feedback")
    if feedback and feedback != "APPROVED":
        print("Engineer is revising based on feedback...")
        revised_description = f"""
        Original Description:
        {description}

        Previous attempt failed. Please correct your code based on this feedback:
        {feedback}
        """
        latex_code = get_tikz_engineer_response(revised_description)
    else:
        latex_code = get_tikz_engineer_response(description)
    
    print("\n--- Generated LaTeX Code ---\n", latex_code, "\n--------------------------\n")
    
    # 编译 LaTeX 代码
    output_base = f"outputs/geometry_v{current_iteration + 1}"
    compilation_result = compile_latex_code(latex_code, output_base)
    
    saved_files = state["saved_files"]
    if compilation_result["success"]:
        pdf_path = compilation_result["path"]
        saved_files.append(pdf_path)
        print(f"✅ PDF file successfully generated at: {pdf_path}")
    else:
        print(f"❌ LaTeX compilation failed.")
        print(f"Error details: {compilation_result['error']}")

    # 保存本次迭代的文件路径以供反馈
    return {
        "latex_code": latex_code,
        "compilation_result": compilation_result,
        "iteration_count": current_iteration + 1,
        "saved_files": saved_files,
        "last_pdf_path": f"{output_base}.pdf",
        "last_log_path": f"{output_base}.log"
    }

def critic_node(state: AgentState) -> AgentState:
    """审查员节点"""
    print("--- NODE: CRITIC ---")
    description = state["structured_description"]
    code = state["latex_code"]
    result = state["compilation_result"]
    
    # 直接将所有信息传递给新的审查员
    feedback = get_tikz_critic_response(description, code, result)
    
    return {"critic_feedback": feedback}

# --- 定义条件边 ---

def should_continue_edge(state: AgentState) -> str:
    """决定是结束还是返回诊断分析师进行修改"""
    print("--- DECISION: SHOULD CONTINUE? ---")
    feedback = state["critic_feedback"]
    count = state["iteration_count"]

    if feedback == "APPROVED":
        print("DECISION: Workflow approved. Finishing.")
        return "end"
    elif count >= MAX_ITERATIONS:
        print(f"DECISION: Max iterations ({MAX_ITERATIONS}) reached. Finishing.")
        return "end"
    else:
        print(f"DECISION: Revisions needed. Going to triage analyst (Iteration {count}).")
        return "revise"

# --- 构建图 (新结构) ---
def build_workflow():
    workflow = StateGraph(AgentState)

    # 添加所有节点
    workflow.add_node("initial_analyst", initial_analyst_node)
    workflow.add_node("triage_analyst", triage_analyst_node)
    workflow.add_node("engineer", engineer_node)
    workflow.add_node("critic", critic_node)

    # 设置入口点
    workflow.set_entry_point("initial_analyst")

    # 定义图的边
    workflow.add_edge("initial_analyst", "engineer")
    workflow.add_edge("triage_analyst", "engineer")  # 诊断后也去工程师那里
    workflow.add_edge("engineer", "critic")
    
    # 定义条件边 (这是核心改动)
    workflow.add_conditional_edges(
        "critic",
        should_continue_edge,
        {
            "revise": "triage_analyst",  # 失败后去"会诊"，而不是直接返工
            "end": END
        }
    )

    app = workflow.compile()
    print("✅ Workflow compiled successfully with triage loop.")
    return app
