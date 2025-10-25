from mem0 import Memory
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


print("Loading environment...")
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("API key loaded?", bool(OPENAI_API_KEY))

client = OpenAI(api_key=OPENAI_API_KEY)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-small"}
    },
    "llm": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"}
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333
        }
    }
}

print("Initializing Memory client...")
mem_client = Memory.from_config(config)
print("Memory client initialized ✅")

while True:
    user_query = input("> ")

    search_memory=mem_client.search(query=user_query,user_id="dhiman")

    memories=[
        f"ID: {mem.get("id")}\nMemory: {mem.get("memory")}" for mem in search_memory.get("results")
    ]

    print("Found Memories",memories)

    SYSTEM_PROMPT=f"""
        here is the context about the user:
        {json.dumps(memories)}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"system","content":SYSTEM_PROMPT},{"role": "user", "content": user_query}]
    )

    ai_response = response.choices[0].message.content
    print("AI:", ai_response)

    mem_client.add(
        user_id="dhiman",
        messages=[
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": ai_response}
        ]
    )

    print("Memory has been saved ✅")
