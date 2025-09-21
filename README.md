# 几何图形矢量化智能体系统 (Geometric Figure Vectorization Agent System)

本项目利用 LangChain 和 LangGraph 框架，构建一个先进的多智能体（Multi-Agent）系统，能够将自然语言或手绘草图中的几何描述，转换成出版物级别的、高精度的 PDF 矢量图形。

## 核心原理与架构

传统的代码生成智能体在处理需要高精度逻辑的任务时，常常因为上下文理解不全或推理错误而陷入“反复试错-修补”的怪圈。本项目通过重新设计智能体的职责，从根本上解决了这一问题。

系统的核心由两个关键智能体驱动，遵循一个更稳健的“认知-执行”工作流：

### 1. 几何构建规划师 (Geometric Construction Planner)

* **角色**: 系统的“数学家”和“大脑”。

* **任务**: 接收用户的原始需求，并进行深入的几何推理。它不直接生成绘图代码，而是输出一份**分步的、基于坐标的“几何构建计划” (JSON格式)**。

* **产出示例**: 对于“绘制一个等腰三角形ABC，AB=AC=5，BC=6”的需求，它会输出类似如下的计划：

  ```json
  {
    "show_axes": false,
    "construction_plan": [
      {
        "step": 1,
        "reasoning": "将底边BC的中点M设为坐标原点(0,0)以简化计算。",
        "instruction": "定义点M为坐标(0,0)。"
      },
      {
        "step": 2,
        "reasoning": "BC=6，所以B在(-3,0)，C在(3,0)。",
        "instruction": "定义点B为坐标(-3,0)，点C为坐标(3,0)。"
      },
      {
        "step": 3,
        "reasoning": "根据勾股定理，高度 AM = sqrt(5^2 - 3^2) = 4。",
        "instruction": "定义顶点A的坐标为(0,4)。"
      },
      {
        "step": 4,
        "reasoning": "连接所有顶点。",
        "instruction": "使用'draw'命令连接点A, B, C，形成闭合路径。"
      }
    ]
  }
  ```

  * **优势**:

      * **可解释性**: `reasoning` 字段让AI的思考过程完全透明。

      * **精确性**: 所有复杂的数学计算都在此环节完成，确保了逻辑的正确性。

### 2\. TikZ 代码翻译官 (TikZ Code Translator)

  * **角色**: 系统的“代码工人”和“双手”。

  * **任务**: 接收“几何构建规划师”生成的JSON计划，并将其**忠实地、逐条地**翻译成 LaTeX/TikZ 代码。它不进行任何创造性思考或几何推理。

  * **优势**:

      * **可靠性**: 任务单一且明确，极大降低了生成错误代码的概率。

      * **一致性**: 严格遵循规划，确保最终图形与规划意图完全一致。

### 3\. 反馈与修正循环 (Feedback & Triage Loop)

当编译失败或审查员发现最终的PDF不符合预期时，反馈信息（包括审查员意见、PDF截图、编译日志）会被\*\*优先发回给“几何构建规划师”**进行“会诊”。规划师会判断是自己的**规划（JSON）**出了问题，还是**翻译（.tex代码）\*\*环节出了问题，从而进行根本性的修正。

这个**认知层**的反馈循环，使得系统具备了强大的自我反思和深度调试能力。

## 目录结构

```
geometric-agent-system/
│
├── agents/                 # 存放每个智能体核心逻辑的模块
│   ├── analyst.py          # 几何构建规划师
│   ├── tikz_critic.py      # 审查员
│   └── tikz_engineer.py    # TikZ代码翻译官
│
├── outputs/                # 存放生成的 .tex, .log, .pdf 等文件
│
├── tools/                  # 存放智能体使用的工具
│   ├── latex_compiler.py   # LaTeX 编译器工具
│   └── pdf_utils.py        # PDF转图片工具，用于反馈循环
│
├── config.py               # 负责加载和管理配置文件
├── config.yaml             # LLM API密钥、模型名称等配置
├── main.py                 # 项目主入口，负责启动和运行工作流
├── prompts.py              # 集中管理所有智能体的Prompt
├── workflow.py             # 定义LangGraph工作流（状态、节点、边）
│
├── README.md               # 本文档
└── requirements.txt        # 项目所需的Python依赖库
```

## 安装与使用

### 1\. 前置条件

**最重要的一步**: 您的系统中**必须**安装一个完整的 LaTeX 发行版，并确保 `pdflatex` 命令可以在系统的 PATH 环境变量中被访问到。

  * **Windows**: [MiKTeX](https://miktex.org/)

  * **macOS**: [MacTeX](https://www.tug.org/mactex/)

  * **Linux/跨平台**: [TeX Live](https://www.tug.org/texlive/)

您可以在终端或命令行中运行 `pdflatex --version` 来检查是否安装成功。

### 2\. 安装步骤

1.  **克隆仓库**

    ```bash
    git clone <your-repository-url>
    cd geometric-agent-system
    ```

2.  **创建并激活Conda虚拟环境**

    ```bash
    # 推荐指定一个Python版本，例如 3.12
    conda create -n mathsvg python=3.12
    conda activate mathsvg
    ```

3.  **安装依赖库**

    ```bash
    pip install -r requirements.txt
    ```

4.  **配置API**
    打开 `config.yaml` 文件，填入您的LLM API密钥和模型名称。

    ```yaml
    api_key: "YOUR_API_KEY_HERE"
    base_url: "[https://api.siliconflow.cn/v1](https://api.siliconflow.cn/v1)" # 或您的API地址
    multimodal_model: "Qwen/Qwen2.5-VL-72B-Instruct"
    text_model: "Qwen/Qwen2.5-7B-Instruct" # 或其它高性能文本模型
    ```

### 3\. 运行项目

1.  **启动程序**

    ```bash
    python main.py
    ```

2.  **输入需求**
    程序启动后，会提示您输入几何图形的描述。您可以输入纯文本，例如：

    > `绘制一个等腰三角形ABC，其中AB = AC = 5，底边BC = 6`

    或者：

    > `一个直角坐标系。在第一象限，有一个矩形ABCD。点A是坐标原点(0,0)。点B在X轴上，点D在Y轴上。AB的长度是200，AD的长度是100。在矩形内，画一条从A点到C点的对角线。`

3.  **查看结果**
    智能体系统将开始工作，并在终端实时打印每一步的进展。

      * 所有生成的中间文件（`.tex`, `.log`）和最终产物（`.pdf`）都会保存在 `outputs/` 目录下。

      * 即使修正过程经历了多次迭代（v1, v2, v3...），所有成功生成的PDF版本都会被保留下来。

      * 工作流结束后，程序会报告最终是否成功，并列出所有成功生成的PDF文件路径。

## 未来扩展

  * 支持在config.yaml中自定义更多，例如模型temprature

  * output目录下支持自动建立时间+标题的格式子目录，存放该次任务的产物

  * 引入”用户介入“功能，可以直接打断agent，提出终止或提出用户自己的意见

  - 图到文的转换

  * **图形化反馈**: 用户通过在生成的PDF/图片上进行标注，来发起新一轮的修正请求。

  * **支持更复杂的几何约束**: 扩展分析师的知识库，使其能够处理更高级的几何问题（如相切、内接/外接圆、三维图形等）。

  * **Web界面**: 为系统创建一个简单的Web UI，让用户可以更方便地提交请求和查看结果。

<!-- end list -->