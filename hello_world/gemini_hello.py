from google import genai

client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how ai works in a few words"
)

print(response.text)
