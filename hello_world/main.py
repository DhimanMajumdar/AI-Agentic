from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are an expert in maths and only ans maths realted stuff. If anything except maths related is asked to you, just say sorry.",
        },
        {
            "role": "user",
            "content": "Hey can you help me solve the a+b whole square stuff.",
        },
    ],
)

print(response.choices[0].message.content)
