import time

from agents.planner_agent import planner_agent
from agents.retriever_agent import retriever_agent
from agents.writer_agent import writer_agent
from agents.critic_agent import critic_agent
from agents.revision_agent import revision_agent
from workflow.logger import save_run_log


def run_multi_agent(user_query: str, task_type: str) -> dict:
    """
    多智能体主调度器。
    执行顺序：
    Planner → Retriever → Writer → Critic → Revision
    """

    total_start = time.perf_counter()
    timing = {}

    start = time.perf_counter()
    plan = planner_agent(user_query, task_type)
    timing["planner_time"] = time.perf_counter() - start

    start = time.perf_counter()
    evidence = retriever_agent(user_query)
    timing["retriever_time"] = time.perf_counter() - start

    start = time.perf_counter()
    draft = writer_agent(user_query, plan, evidence)
    timing["writer_time"] = time.perf_counter() - start

    start = time.perf_counter()
    critique = critic_agent(draft)
    timing["critic_time"] = time.perf_counter() - start

    start = time.perf_counter()
    final_answer = revision_agent(draft, critique)
    timing["revision_time"] = time.perf_counter() - start

    timing["total_time"] = time.perf_counter() - total_start

    result = {
        "plan": plan,
        "evidence": evidence,
        "draft": draft,
        "critique": critique,
        "final_answer": final_answer,
        "timing": timing
    }

    log_paths = save_run_log(
        user_query=user_query,
        task_type=task_type,
        result=result,
        timing=timing
    )

    result["log_paths"] = log_paths

    return result