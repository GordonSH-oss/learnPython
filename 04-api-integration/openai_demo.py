from openai import OpenAI

client = OpenAI(
    api_key="sk-1d07f69b9c80d5cab76f1081b8e95977e89ae762f32bcaa9814de8c7e3bbae3f",
    base_url="https://api-xmodel.rongcloud.cn/v1"
)

response = client.chat.completions.create(
    model="deepseek-v3",  # 使用更常见的模型，或者咨询 API 提供商支持哪些模型
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)