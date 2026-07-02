import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import json
import csv
import time
from datetime import datetime

from workflow.orchestrator import run_multi_agent
from evaluation.baseline import run_single_agent


def load_test_cases() -> list:
    """
    读取测试任务集。
    """
    test_case_path = Path("evaluation") / "test_cases.json"

    if not test_case_path.exists():
        raise FileNotFoundError("未找到 evaluation/test_cases.json，请先创建测试任务集。")

    with open(test_case_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_evaluation_results(results: list) -> dict:
    """
    保存实验结果。
    同时保存 JSON、CSV 和 Markdown 三种格式。
    """

    output_dir = Path("outputs") / "evaluation_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"evaluation_{timestamp}.json"
    csv_path = output_dir / f"evaluation_{timestamp}.csv"
    md_path = output_dir / f"evaluation_{timestamp}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id",
            "task_type",
            "system_type",
            "total_time",
            "user_query",
            "final_answer_preview",
            "log_json",
            "log_md"
        ])

        for item in results:
            writer.writerow([
                item.get("case_id", ""),
                item.get("task_type", ""),
                item.get("system_type", ""),
                f'{item.get("total_time", 0):.2f}',
                item.get("user_query", ""),
                item.get("final_answer", "")[:200].replace("\n", " "),
                item.get("log_paths", {}).get("json_path", ""),
                item.get("log_paths", {}).get("md_path", "")
            ])

    md_lines = [
        "# 单 Agent 与多 Agent 对比实验结果",
        "",
        f"**实验时间：** {timestamp}",
        "",
        "## 一、实验说明",
        "",
        "本实验使用相同测试任务分别运行单 Agent Baseline 和多智能体系统，并记录最终输出、运行耗时和日志路径。",
        "",
        "## 二、实验结果概览",
        "",
        "| 测试编号 | 任务类型 | 系统类型 | 总耗时 |",
        "|---|---|---|---:|"
    ]

    for item in results:
        md_lines.append(
            f"| {item.get('case_id', '')} | {item.get('task_type', '')} | "
            f"{item.get('system_type', '')} | {item.get('total_time', 0):.2f} 秒 |"
        )

    md_lines.extend([
        "",
        "## 三、详细结果",
        ""
    ])

    for item in results:
        md_lines.extend([
            f"### {item.get('case_id', '')} - {item.get('system_type', '')}",
            "",
            f"**任务类型：** {item.get('task_type', '')}",
            "",
            "**用户输入：**",
            "",
            item.get("user_query", ""),
            "",
            f"**总耗时：** {item.get('total_time', 0):.2f} 秒",
            "",
            "**最终输出：**",
            "",
            item.get("final_answer", ""),
            "",
            "---",
            ""
        ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return {
        "json_path": str(json_path),
        "csv_path": str(csv_path),
        "md_path": str(md_path)
    }


def run_evaluation(max_cases: int | None = None) -> dict:
    """
    执行对比实验。
    每个测试任务都会运行：
    1. 单 Agent Baseline
    2. 多智能体系统
    """

    test_cases = load_test_cases()

    if max_cases is not None:
        test_cases = test_cases[:max_cases]

    all_results = []

    for case in test_cases:
        case_id = case["id"]
        task_type = case["task_type"]
        user_query = case["user_query"]

        print(f"\n正在运行测试任务：{case_id} - 单 Agent Baseline")

        baseline_result = run_single_agent(user_query, task_type)

        all_results.append({
            "case_id": case_id,
            "task_type": task_type,
            "system_type": "single_agent_baseline",
            "user_query": user_query,
            "expected_focus": case.get("expected_focus", []),
            "total_time": baseline_result.get("timing", {}).get("total_time", 0),
            "final_answer": baseline_result.get("final_answer", ""),
            "log_paths": baseline_result.get("log_paths", {})
        })

        time.sleep(1)

        print(f"正在运行测试任务：{case_id} - 多智能体系统")

        multi_agent_result = run_multi_agent(user_query, task_type)

        all_results.append({
            "case_id": case_id,
            "task_type": task_type,
            "system_type": "multi_agent_system",
            "user_query": user_query,
            "expected_focus": case.get("expected_focus", []),
            "total_time": multi_agent_result.get("timing", {}).get("total_time", 0),
            "planner_time": multi_agent_result.get("timing", {}).get("planner_time", 0),
            "retriever_time": multi_agent_result.get("timing", {}).get("retriever_time", 0),
            "writer_time": multi_agent_result.get("timing", {}).get("writer_time", 0),
            "critic_time": multi_agent_result.get("timing", {}).get("critic_time", 0),
            "revision_time": multi_agent_result.get("timing", {}).get("revision_time", 0),
            "final_answer": multi_agent_result.get("final_answer", ""),
            "plan": multi_agent_result.get("plan", ""),
            "evidence": multi_agent_result.get("evidence", ""),
            "draft": multi_agent_result.get("draft", ""),
            "critique": multi_agent_result.get("critique", ""),
            "log_paths": multi_agent_result.get("log_paths", {})
        })

        time.sleep(1)

    saved_paths = save_evaluation_results(all_results)

    return {
        "num_cases": len(test_cases),
        "num_runs": len(all_results),
        "saved_paths": saved_paths
    }


if __name__ == "__main__":
    # 第一次建议只跑 1 个测试任务，确认流程没问题。
    summary = run_evaluation(max_cases=None)

    print("\n实验运行完成。")
    print(f"测试任务数：{summary['num_cases']}")
    print(f"总运行次数：{summary['num_runs']}")
    print("结果文件：")
    print(summary["saved_paths"])