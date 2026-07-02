import json
import time
from datetime import datetime
from pathlib import Path

from llm_client import call_llm


def save_baseline_log(
    user_query: str,
    task_type: str,
    answer: str,
    timing: dict
) -> dict:
    """
    保存单 Agent Baseline 的运行日志。
    """

    log_dir = Path("outputs") / "baseline_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = log_dir / f"baseline_{timestamp}.json"
    md_path = log_dir / f"baseline_{timestamp}.md"

    log_data = {
        "timestamp": timestamp,
        "system_type": "single_agent_baseline",
        "user_query": user_query,
        "task_type": task_type,
        "timing": timing,
        "final_answer": answer
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    md_content = "\n\n".join([
        "# 单 Agent Baseline 运行日志",
        "## 一、基本信息",
        f"**运行时间：** {timestamp}",
        f"**任务类型：** {task_type}",
        "**用户输入：**",
        user_query,
        "---",
        "## 二、运行耗时",
        f"总耗时：{timing.get('total_time', 0):.2f} 秒",
        "---",
        "## 三、最终输出结果",
        answer
    ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {
        "json_path": str(json_path),
        "md_path": str(md_path)
    }


def run_single_agent(user_query: str, task_type: str) -> dict:
    """
    单 Agent Baseline。
    不进行任务拆解、资料检索、质量检查，直接让大模型回答。
    """

    system_prompt = """
你是一个学术研究助手。请根据用户输入，直接生成结构化学术内容。

要求：
1. 围绕用户原始需求回答；
2. 使用清晰的 Markdown 结构；
3. 内容适合作为项目报告或研究计划初稿；
4. 不要编造具体实验结果；
5. 不要声称已经完成真实系统部署；
6. 不要输出 Agent 执行过程，只输出最终内容。
"""

    user_prompt = f"""
任务类型：
{task_type}

用户需求：
{user_query}

请直接生成最终回答。
"""

    start = time.perf_counter()
    answer = call_llm(system_prompt, user_prompt, temperature=0.3)
    total_time = time.perf_counter() - start

    timing = {
        "total_time": total_time
    }

    log_paths = save_baseline_log(
        user_query=user_query,
        task_type=task_type,
        answer=answer,
        timing=timing
    )

    return {
        "final_answer": answer,
        "timing": timing,
        "log_paths": log_paths
    }