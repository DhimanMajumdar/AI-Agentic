from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

# Zero-shot prompting: The model is given a direct ques or task withput prior examples.
SYSTEM_PROMPT = "You should only ans the coding realted ques. Do not an anything else. Your name is Bunny. if anyone ask anything except coding ques, juts say sorry, ask coding realted stuffs only."

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": "Hey can you tell me Prime Minister of India.",
        },
    ],
)

print(response.choices[0].message.content)
