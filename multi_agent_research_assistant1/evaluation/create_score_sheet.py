import json
import csv
from datetime import datetime
from pathlib import Path


def find_latest_evaluation_json() -> Path:
    result_dir = Path("outputs") / "evaluation_results"

    json_files = sorted(
        result_dir.glob("evaluation_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if not json_files:
        raise FileNotFoundError("未找到 outputs/evaluation_results/evaluation_*.json，请先运行实验。")

    return json_files[0]


def create_score_sheet() -> dict:
    latest_json = find_latest_evaluation_json()

    with open(latest_json, "r", encoding="utf-8") as f:
        results = json.load(f)

    output_dir = Path("outputs") / "score_sheets"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = output_dir / f"score_sheet_{timestamp}.csv"

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "case_id",
            "task_type",
            "system_type",
            "total_time",
            "user_query",
            "final_answer_preview",
            "task_completion_score",
            "structure_score",
            "accuracy_score",
            "logic_score",
            "explainability_score",
            "executability_score",
            "total_score",
            "comments"
        ])

        for item in results:
            writer.writerow([
                item.get("case_id", ""),
                item.get("task_type", ""),
                item.get("system_type", ""),
                f'{item.get("total_time", 0):.2f}',
                item.get("user_query", ""),
                item.get("final_answer", "")[:300].replace("\n", " "),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                ""
            ])

    return {
        "input_json": str(latest_json),
        "score_sheet": str(csv_path)
    }


if __name__ == "__main__":
    paths = create_score_sheet()

    print("评分表已生成。")
    print("读取的实验结果文件：")
    print(paths["input_json"])
    print("生成的评分表：")
    print(paths["score_sheet"])