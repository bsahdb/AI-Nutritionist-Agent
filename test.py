import os
from openai import OpenAI

DEEPSEEK_API_KEY = "sk-bb9a2e1a7ce545ce9169ec906a50f0cb"
DEEPSEEK_API_URL = "https://api.deepseek.com"
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_URL
)

response = client.chat.completions.create(
    model = "deepseek-v4-flash",
    messages = [
        {"role": "system", "content": "你是一个有用的助手，帮助用户查询天气并生成提醒。"},
        {"role": "user", "content": "Hello"}
    ],
    stream = False
)
print(response.choices[0].message.content)