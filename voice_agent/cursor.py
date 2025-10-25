from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import requests
from pydantic import BaseModel, Field
from typing import Optional
import json
import os
import asyncio
import speech_recognition as sr
from openai.helpers import LocalAudioPlayer

load_dotenv()

client = OpenAI()
async_client = AsyncOpenAI()

async def tts(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        instructions="Always speak in cheerful manner with full of delight and happy",
        input=speech,
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

def run_command(cmd: str):
    result = os.system(cmd)
    return result

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    return "Something went wrong"

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}

SYSTEM_PROMPT = """
    You're an expert AI Assistant in resolving user queries using chain of thought.
    You work on START, PLAN and OUTPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call a tool if required from the list of available tools.
    for every tool call wait for the observe step which is the output from the called tool.

    Rules:
    - Strictly Follow the given JSON output format
    - Only run one step at a time.
    - The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally OUTPUT (which is going to the displayed to the user).
    Output JSON Format:
    { "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string" }
    Available Tools:
    - get_weather(city: str): Takes city name as an input string and returns the weather info about the city.
    - run_command(cmd: str): Takes a system linux command as string and executes the command on user's system and returns the output from that command
"""

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")

message_history = [
    { "role": "system", "content": SYSTEM_PROMPT },
]

r = sr.Recognizer()
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)
    r.pause_threshold = 2

    while True:
        print("Speak Something...")
        audio = r.listen(source)
        print("Processing Audio... (STT)")
        user_query = r.recognize_google(audio)
        message_history.append({ "role": "user", "content": user_query })

        while True:
            response = client.chat.completions.parse(
                model="gpt-4.1",
                response_format=MyOutputFormat,
                messages=message_history
            )
            raw_result = response.choices[0].message.content
            message_history.append({"role": "assistant", "content": raw_result})
            parsed_result = response.choices[0].message.parsed

            if parsed_result.step == "START":
                print("🔥", parsed_result.content)
                continue

            if parsed_result.step == "TOOL":
                tool_to_call = parsed_result.tool
                tool_input = parsed_result.input
                print(f"🛠️: {tool_to_call} ({tool_input})")

                tool_response = available_tools[tool_to_call](tool_input)
                print(f"🛠️: {tool_to_call} ({tool_input}) = {tool_response}")
                message_history.append({ "role": "developer", "content": json.dumps(
                    { "step": "OBSERVE", "tool": tool_to_call, "input": tool_input, "output": tool_response}
                ) })
                continue

            if parsed_result.step == "PLAN":
                print("🧠", parsed_result.content)
                continue

            if parsed_result.step == "OUTPUT":
                print("🤖", parsed_result.content)

                # Heuristic to decide which file to write to
                content = parsed_result.content or ""
                if "<html" in content.lower() or "<!doctype html" in content.lower():
                    file_target = "index.html"
                elif content.strip().startswith((".", "#", "body", "html", "div")) or "{" in content:
                    file_target = "styles.css"
                elif any(js_kw in content for js_kw in ["function ", "console.log", "document.", "let ", "const ", "var "] ):
                    file_target = "script.js"
                else:
                    file_target = "misc_output.txt"

                with open(file_target, "a", encoding="utf-8") as file:
                    file.write(content + "\n")

                asyncio.run(tts(speech=content))
                break
