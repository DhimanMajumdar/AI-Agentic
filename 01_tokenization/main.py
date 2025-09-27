import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hey There! My name is Dhiman Majumdar"
tokens = enc.encode(text)

# Tokens: [25216, 3274, 0, 3673, 1308, 382, 31129, 30576, 18968, 394, 38450]
print("Tokens:", tokens)

decoded = enc.decode([25216, 3274, 0, 3673, 1308, 382, 31129, 30576, 18968, 394, 38450])
print("Decoded", decoded)
