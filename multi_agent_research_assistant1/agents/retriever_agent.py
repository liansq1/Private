import json
from pathlib import Path
from llm_client import call_llm


def load_knowledge_base() -> list:
    """
    读取本地知识库文件。
    """
    kb_path = Path("data") / "knowledge_base.json"

    if not kb_path.exists():
        raise FileNotFoundError("未找到 data/knowledge_base.json，请先创建本地知识库文件。")

    with open(kb_path, "r", encoding="utf-8") as f:
        return json.load(f)


def simple_retrieve(user_query: str, knowledge_base: list, top_k: int = 5) -> list:
    """
    简单关键词匹配检索。
    第一版不做向量数据库，先用关键词匹配完成可运行原型。
    """
    query = user_query.lower()
    scored_items = []

    for item in knowledge_base:
        score = 0

        title = item.get("title", "").lower()
        content = item.get("content", "").lower()
        keywords = item.get("keywords", [])

        if title in query:
            score += 3

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in query:
                score += 2
            if keyword_lower in content:
                score += 1

        scored_items.append((score, item))

    scored_items.sort(key=lambda x: x[0], reverse=True)

    selected = [item for score, item in scored_items if score > 0][:top_k]

    # 如果没有匹配到，就默认取前 top_k 条，避免 Retriever 没有资料可用
    if not selected:
        selected = knowledge_base[:top_k]

    return selected


def retriever_agent(user_query: str) -> str:
    knowledge_base = load_knowledge_base()
    retrieved_items = simple_retrieve(user_query, knowledge_base)

    retrieved_text = "\n\n".join(
        [
            f"资料标题：{item['title']}\n资料内容：{item['content']}"
            for item in retrieved_items
        ]
    )

    system_prompt = """
你是 Retriever Agent，负责为学术研究任务整理相关资料和支撑信息。

你现在已经获得了本地知识库检索结果。
你的任务是：
1. 阅读本地知识库检索结果；
2. 提取与用户任务最相关的概念、技术和研究线索；
3. 不要编造具体论文、作者、年份或实验数据；
4. 输出内容要服务于后续 Writer Agent；
5. 明确说明资料来自“本地知识库”。

输出格式：
### Retriever Agent：资料整理结果

#### 1. 使用的本地知识库资料
- ……

#### 2. 核心概念
……

#### 3. 关键技术
……

#### 4. 对后续写作的支撑作用
……

#### 5. 可进一步扩展的资料方向
……
"""

    user_prompt = f"""
用户研究任务：
{user_query}

本地知识库检索结果：
{retrieved_text}

请基于以上本地知识库资料，整理与用户任务相关的资料线索。
"""

    return call_llm(system_prompt, user_prompt, temperature=0.2)