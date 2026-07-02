import os
import streamlit as st
from datetime import datetime

from workflow.orchestrator import run_multi_agent
from evaluation.baseline import run_single_agent


st.set_page_config(
    page_title="面向学术研究的 AI 助手",
    page_icon="🧠",
    layout="wide"
)

# =========================
# 样式设置
# =========================
st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #1f2430;
        margin-bottom: 6px;
    }

    .sub-title {
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 24px;
    }

    .answer-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px 18px;
        margin-top: 8px;
        margin-bottom: 12px;
        border: 1px solid #e5e7eb;
    }

    .process-box {
        background-color: #f9fafb;
        border-radius: 10px;
        padding: 12px 14px;
        border: 1px solid #e5e7eb;
        color: #6b7280;
        font-size: 13px;
        line-height: 1.6;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    .meta-text {
        color: #9ca3af;
        font-size: 12px;
        margin-top: 4px;
        margin-bottom: 10px;
    }

    .history-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 12px;
        color: #1f2430;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# session_state 初始化
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

# =========================
# 标题
# =========================
st.markdown('<div class="main-title">面向学术研究的 AI 助手</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">帮助你完成研究主题解释、研究计划、系统架构设计、技术路线与实验评测方案。</div>',
    unsafe_allow_html=True
)

# =========================
# 侧边栏
# =========================
with st.sidebar:
    st.header("任务设置")

    run_mode = st.radio(
        "请选择使用模式",
        [
            "标准模式（结果更完整）",
            "快速模式（生成更快）"
        ]
    )

    task_type = st.selectbox(
        "请选择任务类型",
        [
            "研究主题解释",
            "研究计划生成",
            "文献综述初稿",
            "系统架构设计",
            "技术路线生成",
            "实验评测方案"
        ]
    )

    show_process = st.checkbox("显示系统处理过程", value=True)

    st.divider()
    st.caption("当前运行目录")
    st.code(os.getcwd())

    st.divider()

    if st.button("清空当前对话"):
        st.session_state.chat_history = []
        st.rerun()

# =========================
# 历史对话展示
# =========================
if st.session_state.chat_history:
    st.markdown('<div class="history-title">对话记录</div>', unsafe_allow_html=True)

for i, item in enumerate(st.session_state.chat_history):
    # 用户问题
    with st.chat_message("user"):
        st.markdown(item["user_query"])

    # 助手回答
    with st.chat_message("assistant"):
        st.markdown(
            f"""
<div class="meta-text">
模式：{item["run_mode"]} ｜ 任务类型：{item["task_type"]} ｜ 时间：{item["timestamp"]}
</div>
""",
            unsafe_allow_html=True
        )

        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown(item["result"].get("final_answer", ""))
        st.markdown('</div>', unsafe_allow_html=True)

        if show_process and item["run_mode"] == "标准模式（结果更完整）":
            with st.expander("查看系统处理过程", expanded=False):
                st.markdown('<div class="process-box">', unsafe_allow_html=True)

                st.markdown("**1. 任务理解与拆解**")
                st.markdown(item["result"].get("plan", ""))

                st.markdown("**2. 资料整理**")
                st.markdown(item["result"].get("evidence", ""))

                st.markdown("**3. 初稿生成**")
                st.markdown(item["result"].get("draft", ""))

                st.markdown("**4. 质量检查**")
                st.markdown(item["result"].get("critique", ""))

                st.markdown('</div>', unsafe_allow_html=True)

        timing = item["result"].get("timing", {})
        log_paths = item["result"].get("log_paths", {})

        with st.expander("查看运行信息", expanded=False):
            if item["run_mode"] == "标准模式（结果更完整）":
                st.markdown(
                    f"""
**总耗时：** {timing.get("total_time", 0):.2f} 秒

**各环节耗时：**

| 环节 | 耗时 |
|---|---:|
| 任务规划 | {timing.get("planner_time", 0):.2f} 秒 |
| 资料整理 | {timing.get("retriever_time", 0):.2f} 秒 |
| 内容生成 | {timing.get("writer_time", 0):.2f} 秒 |
| 质量检查 | {timing.get("critic_time", 0):.2f} 秒 |
| 结果修订 | {timing.get("revision_time", 0):.2f} 秒 |

**日志文件路径：**
- JSON：`{log_paths.get("json_path", "")}`
- Markdown：`{log_paths.get("md_path", "")}`
"""
                )
            else:
                st.markdown(
                    f"""
**总耗时：** {timing.get("total_time", 0):.2f} 秒

**日志文件路径：**
- JSON：`{log_paths.get("json_path", "")}`
- Markdown：`{log_paths.get("md_path", "")}`
"""
                )

# =========================
# 底部输入框
# =========================
user_input = st.chat_input("请输入你的研究问题，例如：帮我生成这个课题的系统架构设计。")

if user_input:
    st.session_state.pending_input = user_input
    st.rerun()

# =========================
# 执行任务
# =========================
if st.session_state.pending_input:
    user_query = st.session_state.pending_input

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("系统正在思考，请稍等..."):
            if run_mode == "标准模式（结果更完整）":
                result = run_multi_agent(user_query, task_type)
            else:
                result = run_single_agent(user_query, task_type)

        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown(result.get("final_answer", ""))
        st.markdown('</div>', unsafe_allow_html=True)

        if show_process and run_mode == "标准模式（结果更完整）":
            with st.expander("查看系统处理过程", expanded=False):
                st.markdown('<div class="process-box">', unsafe_allow_html=True)

                st.markdown("**1. 任务理解与拆解**")
                st.markdown(result.get("plan", ""))

                st.markdown("**2. 资料整理**")
                st.markdown(result.get("evidence", ""))

                st.markdown("**3. 初稿生成**")
                st.markdown(result.get("draft", ""))

                st.markdown("**4. 质量检查**")
                st.markdown(result.get("critique", ""))

                st.markdown('</div>', unsafe_allow_html=True)

        timing = result.get("timing", {})
        log_paths = result.get("log_paths", {})

        with st.expander("查看运行信息", expanded=False):
            if run_mode == "标准模式（结果更完整）":
                st.markdown(
                    f"""
**总耗时：** {timing.get("total_time", 0):.2f} 秒

**各环节耗时：**

| 环节 | 耗时 |
|---|---:|
| 任务规划 | {timing.get("planner_time", 0):.2f} 秒 |
| 资料整理 | {timing.get("retriever_time", 0):.2f} 秒 |
| 内容生成 | {timing.get("writer_time", 0):.2f} 秒 |
| 质量检查 | {timing.get("critic_time", 0):.2f} 秒 |
| 结果修订 | {timing.get("revision_time", 0):.2f} 秒 |

**日志文件路径：**
- JSON：`{log_paths.get("json_path", "")}`
- Markdown：`{log_paths.get("md_path", "")}`
"""
                )
            else:
                st.markdown(
                    f"""
**总耗时：** {timing.get("total_time", 0):.2f} 秒

**日志文件路径：**
- JSON：`{log_paths.get("json_path", "")}`
- Markdown：`{log_paths.get("md_path", "")}`
"""
                )

    # 保存到历史
    st.session_state.chat_history.append(
        {
            "user_query": user_query,
            "task_type": task_type,
            "run_mode": run_mode,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": result
        }
    )

    # 清空待处理输入
    st.session_state.pending_input = None
    st.rerun()