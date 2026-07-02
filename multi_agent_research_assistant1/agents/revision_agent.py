from llm_client import call_llm


def revision_agent(draft: str, critique: str) -> str:
    system_prompt = """
你是 Revision Writer，负责根据 Critic Agent 的检查意见修订初稿。

要求：
1. 保留初稿中合理的内容；
2. 根据 Critic 的建议补充缺失部分；
3. 删除或弱化不准确、过度夸大的表达；
4. 统一术语，必须使用 Planner Agent、Retriever Agent、Writer Agent、Critic Agent；
5. 输出完整的最终版本；
6. 使用 Markdown 结构；
7. 不要解释你修改了什么，直接输出修订后的最终内容。
"""

    user_prompt = f"""
以下是 Writer Agent 的初稿：

{draft}

以下是 Critic Agent 的检查意见：

{critique}

请根据检查意见修订初稿，并输出最终版本。
"""

    return call_llm(system_prompt, user_prompt, temperature=0.3)