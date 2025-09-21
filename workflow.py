# workflow.py
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import json
import os
import datetime  # 新增导入

from agents.analyst import get_analyst_response
from agents.tikz_engineer import get_tikz_engineer_response
from agents.tikz_critic import get_tikz_critic_response

from agents.title_generator import get_title_from_description  # 新增导入
from tools.latex_compiler import compile_latex_code
from tools.logger import initialize_log, log_message  # 新增导入

MAX_ITERATIONS = 5

# 修改 AgentState 类，增加 output_directory 字段

class AgentState(TypedDict):
    """定义工作流的状态"""
    initial_request: dict
    structured_description: str
    output_directory: str
    log_file_path: str  # 新增字段
    latex_code: str
    compilation_result: Dict[str, Any]
    critic_feedback: str
    iteration_count: int
    saved_files: List[str]
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

# 在 initial_analyst_node 和 triage_analyst_node 之间，添加新节点 title_generator_node
def title_generator_node(state: AgentState) -> AgentState:
    """根据描述生成标题并为当前任务创建输出目录。"""
    print("--- NODE: TITLE GENERATOR & DIRECTORY SETUP ---")
    description = state["structured_description"]
    
    # 1. 生成标题
    title = get_title_from_description(description)

    # 2. 创建带时间戳的目录
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"{timestamp}_{title}"
    output_path = os.path.join("outputs", dir_name)

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"✅ Created output directory: {output_path}")

    # 3. 初始化日志文件
    log_path = initialize_log(output_path)

    # 4. 记录上一个节点 (analyst) 的输出
    log_message(log_path, description, title="几何构建规划师 (Analyst) 输出")

    return {"output_directory": output_path, "log_file_path": log_path}

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

    # 记录诊断和修正后的新规划
    log_path = state["log_file_path"] # 获取日志路径
    log_message(log_path, new_description, title=f"会诊规划师 (Triage Analyst) 输出 - 第 {state['iteration_count']} 轮后")

    # 更新状态中的几何描述
    return {"structured_description": new_description}

def engineer_node(state: AgentState) -> AgentState:
    """TikZ工程师节点"""
    print("--- NODE: TIKZ ENGINEER & COMPILER ---")
    description = state["structured_description"]
    current_iteration = state["iteration_count"]
    output_dir = state["output_directory"]
    log_path = state["log_file_path"] # 获取日志路径
    
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
    # 记录生成的代码
    log_message(log_path, latex_code, title=f"代码翻译官 (Engineer) 输出 - 第 {current_iteration + 1} 轮")

    output_base = os.path.join(output_dir, f"geometry_v{current_iteration + 1}")
    compilation_result = compile_latex_code(latex_code, output_base, output_dir)

    # 记录编译结果
    if compilation_result["success"]:
        log_content = f"✅ PDF文件成功生成于: {compilation_result['path']}"
    else:
        log_content = f"❌ LaTeX 编译失败。\n错误详情:\n{compilation_result['error']}"
    log_message(log_path, log_content, title=f"LaTeX 编译器输出 - 第 {current_iteration + 1} 轮")

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
    log_path = state["log_file_path"] # 获取日志路径

    feedback = get_tikz_critic_response(description, code, result)

    # 记录审查员的反馈
    log_message(log_path, feedback, title=f"审查员 (Critic) 反馈 - 第 {state['iteration_count']} 轮")

    return {"critic_feedback": feedback}

# --- 定义条件边 ---

def should_continue_edge(state: AgentState) -> str:
    """决定是结束还是返回诊断分析师进行修改"""
    print("--- DECISION: SHOULD CONTINUE? ---")
    feedback = state["critic_feedback"]
    count = state["iteration_count"]
    log_path = state["log_file_path"] # 获取日志路径

    decision = ""
    if feedback == "APPROVED":
        decision = "end"
        print("DECISION: Workflow approved. Finishing.")
        log_message(log_path, "流程被批准。任务结束。", title="决策")
    elif count >= MAX_ITERATIONS:
        decision = "end"
        print(f"DECISION: Max iterations ({MAX_ITERATIONS}) reached. Finishing.")
        log_message(log_path, f"已达到最大迭代次数 ({MAX_ITERATIONS})。任务结束。", title="决策")
    else:
        decision = "revise"
        print(f"DECISION: Revisions needed. Going to triage analyst (Iteration {count}).")
        log_message(log_path, f"需要修正。进入“会诊”流程 (第 {count} 轮)。", title="决策")

    return decision

# --- 构建图 (新结构) ---
def build_workflow():
    workflow = StateGraph(AgentState)

    # 添加所有节点
    workflow.add_node("initial_analyst", initial_analyst_node)
    workflow.add_node("title_generator", title_generator_node)  # 新增节点
    workflow.add_node("triage_analyst", triage_analyst_node)
    workflow.add_node("engineer", engineer_node)
    workflow.add_node("critic", critic_node)

    # 设置入口点
    workflow.set_entry_point("initial_analyst")

    # 定义图的边
    workflow.add_edge("initial_analyst", "title_generator")  # 修改：分析师 -> 标题生成器
    workflow.add_edge("title_generator", "engineer")       # 新增：标题生成器 -> 工程师
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
    print("✅ Workflow compiled successfully with title generator and triage loop.")
    return app
