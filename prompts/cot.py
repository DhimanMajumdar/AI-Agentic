from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

client = OpenAI()

# Few-shot prompting: The model is given a direct ques or task with prior examples.
SYSTEM_PROMPT = """
You're an expert AI Assistant in resolving user queries using chain of thought
You work on START, PLAN and OUPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.

Rules:
- Strictly Follow the given JSON output format
- Only run one step at a time.
- The sequence of steps is START (where user gives an input), PLAN (that can be multiple times) and finally OUTPUT (which is going to the displayed to the user).

Output JSON Format:
{ "step": "START" | "PLAN" | "OUTPUT", "content": "string" }

Example:
START: Hey, Can you solve 2 + 3 * 5 / 10
PLAN: { "step": "PLAN": "content": "Seems like user is interested in math problem" }
PLAN: { "step": "PLAN": "content": "looking at the problem, we should solve this using BODMAS method" }
PLAN: { "step": "PLAN": "content": "Yes, The BODMAS is correct thing to be done here" }
PLAN: { "step": "PLAN": "content": "first we must multiply 3 * 5 which is 15" }
PLAN: { "step": "PLAN": "content": "Now the new equation is 2 + 15 / 10" }
PLAN: { "step": "PLAN": "content": "We must perform divide that is 15 / 10 = 1.5" }
PLAN: { "step": "PLAN": "content": "Now the new equation is 2 + 1.5" }
PLAN: { "step": "PLAN": "content": "Now finally lets perform the add 3.5" }
PLAN: { "step": "PLAN": "content": "Great, we have solved and finally left with 3.5 as ans" }
OUTPUT: { "step": "OUTPUT": "content": "3.5" }
"""

print("\n\n\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=message_history,
    )
    raw_result = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw_result})

    parsed_result = json.loads(raw_result)

    if parsed_result.get("step") == "START":
        print("🔥", parsed_result.get("content"))
        continue

    if parsed_result.get("step") == "PLAN":
        print("🧠", parsed_result.get("content"))
        continue

    if parsed_result.get("step") == "OUTPUT":
        print("🔳", parsed_result.get("content"))
        break


print("\n\n\n")


# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     response_format={"type": "json_object"},
#     messages=[
#         {
#             "role": "system",
#             "content": SYSTEM_PROMPT,
#         },
#         {
#             "role": "user",
#             "content": "Hey can you write a code to add n numbers in js.",
#         },
#         # manually keep adding messages to history
#         {
#             "role": "assistant",
#             "content": json.dumps(
#                 {
#                     "step": "START",
#                     "content": "User is requesting a JavaScript code to add n numbers.",
#                 }
#             ),
#         },
#         {
#             "role": "assistant",
#             "content": json.dumps(
#                 {
#                     "step": "PLAN",
#                     "content": "To add n numbers in JavaScript, we need to define a function.",
#                 }
#             ),
#         },
#         {
#             "role": "assistant",
#             "content": json.dumps(
#                 {
#                     "step": "PLAN",
#                     "content": "The function should accept an array of numbers as a parameter and return the sum.",
#                 }
#             ),
#         },
#         {
#             "role": "assistant",
#             "content": json.dumps(
#                 {
#                     "step": "PLAN",
#                     "content": "We'll utilize a loop or the reduce method to iterate through the numbers and calculate the total sum.",
#                 }
#             ),
#         },
#         {
#             "role": "assistant",
#             "content": json.dumps(
#                 {
#                     "step": "PLAN",
#                     "content": "Next, we need to provide an example of how to use this function to add a sample array of numbers.",
#                 }
#             ),
#         },
#     ],
# )

# print(response.choices[0].message.content)
