from llm_client import call_llm


def writer_agent(user_query: str, plan: str, evidence: str) -> str:
    system_prompt = """
你是 Writer Agent，负责根据 Planner Agent 的任务规划和 Retriever Agent 的资料整理结果，生成结构化学术内容。
...
"""

    user_prompt = f"""
用户原始需求：
{user_query}

Planner Agent 的任务规划：
{plan}

Retriever Agent 的资料整理：
{evidence}

请生成一份结构化学术内容初稿。
"""

    return call_llm(system_prompt, user_prompt, temperature=0.3)