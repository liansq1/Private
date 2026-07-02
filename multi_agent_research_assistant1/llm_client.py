import os
from dotenv import load_dotenv
from openai import OpenAI


# 强制读取当前项目目录下的 .env，避免读取旧配置
load_dotenv(override=True)

api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

if not api_key:
    raise ValueError("没有检测到 DEEPSEEK_API_KEY，请检查项目根目录下的 .env 文件。")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """
    统一的大模型调用函数。
    当前使用 DeepSeek API，通过 OpenAI SDK 兼容格式调用。
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=temperature,
        stream=False
    )

    return response.choices[0].message.content