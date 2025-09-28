from fastapi import FastAPI, Body
from ollama import Client

app = FastAPI()
client = Client(host="http://localhost:11434")  # use http not https


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(message: str = Body(..., embed=True, description="The Message")):
    response = client.chat(
        model="gemma:2b", messages=[{"role": "user", "content": message}]
    )
    return {"response": response["message"]["content"]}
