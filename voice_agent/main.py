from dotenv import load_dotenv
import speech_recognition as sr
from openai import OpenAI
import asyncio
from openai import AsyncOpenAI

from openai.helpers import LocalAudioPlayer

load_dotenv()

client=OpenAI()
async_client=AsyncOpenAI()

async def tts(speeech:str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=speeech,
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

def main():
    r=sr.Recognizer() # speech to text

    with sr.Microphone() as source: # mic access
        r.adjust_for_ambient_noise(source) # cutting of background noise
        r.pause_threshold=2 # if user stops for 2 sec, start the recognition
        
        SYSTEM_PROMPT = f"""
            You're an expert voice agent. You are given the transcript of what user has said using voice.
            You need to output as if you are an voice agent and whatever you speak will be converted back to audio using AI and played back to user.
            """


        messages = [
            { "role": "system", "content": SYSTEM_PROMPT },
        ]
        while True:

            print("Speak Something...")
            audio=r.listen(source)

            print("Processing Audio.... (STT)")
            stt=r.recognize_google(audio)

            print("You said...", stt)

            

            messages.append({ "role": "user", "content": stt })

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages
            )


            print("AI response:", response.choices[0].message.content)
            asyncio.run(tts(speeech= response.choices[0].message.content))

main()