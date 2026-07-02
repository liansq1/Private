import json
from datetime import datetime
from pathlib import Path


def save_run_log(user_query: str, task_type: str, result: dict, timing: dict) -> dict:
    """
    保存一次多智能体系统运行日志。
    会同时保存 JSON 文件和 Markdown 文件。
    """

    log_dir = Path("outputs") / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = log_dir / f"run_{timestamp}.json"
    md_path = log_dir / f"run_{timestamp}.md"

    log_data = {
        "timestamp": timestamp,
        "user_query": user_query,
        "task_type": task_type,
        "timing": timing,
        "plan": result.get("plan", ""),
        "evidence": result.get("evidence", ""),
        "draft": result.get("draft", ""),
        "critique": result.get("critique", ""),
        "final_answer": result.get("final_answer", "")
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    md_content = "\n\n".join([
        "# 多智能体运行日志",
        "## 一、基本信息",
        f"**运行时间：** {timestamp}",
        f"**任务类型：** {task_type}",
        "**用户输入：**",
        user_query,
        "---",
        "## 二、Agent 耗时",
        f"Planner Agent：{timing.get('planner_time', 0):.2f} 秒",
        f"Retriever Agent：{timing.get('retriever_time', 0):.2f} 秒",
        f"Writer Agent：{timing.get('writer_time', 0):.2f} 秒",
        f"Critic Agent：{timing.get('critic_time', 0):.2f} 秒",
        f"Revision Agent：{timing.get('revision_time', 0):.2f} 秒",
        f"总耗时：{timing.get('total_time', 0):.2f} 秒",
        "---",
        "## 三、Planner Agent 输出",
        result.get("plan", ""),
        "---",
        "## 四、Retriever Agent 输出",
        result.get("evidence", ""),
        "---",
        "## 五、Writer Agent 初稿",
        result.get("draft", ""),
        "---",
        "## 六、Critic Agent 检查结果",
        result.get("critique", ""),
        "---",
        "## 七、最终输出结果",
        result.get("final_answer", "")
    ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {
        "json_path": str(json_path),
        "md_path": str(md_path)
    }