from dotenv import load_dotenv
from openai import OpenAI
import json
import requests

load_dotenv()

client = OpenAI()


# ------------------- TOOL DEFINITIONS -------------------
def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}"

    return "Something went wrong"


available_tools = {"get_weather": get_weather}


# ------------------- SYSTEM PROMPT -------------------
SYSTEM_PROMPT = """
You're an expert AI Assistant in resolving user queries using chain of thought.
You work on START, PLAN and OUTPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.
You can also call a tool if required from the list of available tools.

Rules:
- Strictly Follow the given JSON output format
- Only run one step at a time.
- The sequence of steps is START (where user gives an input), PLAN (that can be multiple times), TOOL (if needed), OBSERVE (tool response), and finally OUTPUT (which is displayed to the user).

Output JSON Format:
{ "step": "START" | "PLAN" | "TOOL" | "OBSERVE" | "OUTPUT", "content": "string", "tool":"string", "input":"string", "output":"string" }

AVAILABLE TOOLS:
- get_weather: Takes city name as an input string and returns the weather info about the city
"""


# ------------------- MAIN LOOP -------------------
print("\n\n\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

while True:
    user_query = input("👉 ")
    message_history.append({"role": "user", "content": user_query})

    for _ in range(20):  # safety cap
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=message_history,
        )
        raw_result = response.choices[0].message.content

        try:
            parsed_result = json.loads(raw_result)
        except json.JSONDecodeError:
            print("⚠️ Model returned invalid JSON:", raw_result)
            break

        message_history.append({"role": "assistant", "content": raw_result})

        step = parsed_result.get("step")

        if step == "START":
            print("🔥", parsed_result.get("content"))
            continue

        if step == "PLAN":
            print("🧠", parsed_result.get("content"))
            continue

        if step == "TOOL":
            tool_to_call = parsed_result.get("tool")
            tool_input = parsed_result.get("input")
            print(f"🔪 Calling tool: {tool_to_call}({tool_input})")

            tool_response = available_tools[tool_to_call](tool_input)
            print(f"🔪 Response: {tool_response}")

            message_history.append(
                {
                    "role": "developer",
                    "content": json.dumps(
                        {
                            "step": "OBSERVE",
                            "tool": tool_to_call,
                            "input": tool_input,
                            "output": tool_response,
                        }
                    ),
                }
            )
            continue

        if step == "OBSERVE":
            print("👀 Observation:", parsed_result.get("output"))
            continue

        if step == "OUTPUT":
            print("🔳", parsed_result.get("content"))
            break

print("\n\n\n")
