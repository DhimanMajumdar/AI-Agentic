from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI

load_dotenv()

client = OpenAI()

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]

def chatbot(state: State):
    print("ChatBot Node", state)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            { "role": "user", "content": state.get("user_query") }
        ]
    )

    state["llm_output"] = response.choices[0].message.content
    return state

def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    print("Evaluating response quality...", state)

    evaluation_prompt = f"""
    You are a strict response evaluator.
    The assistant just answered this user query:
    Query: "{state['user_query']}"
    Response: "{state['llm_output']}"

    Decide if this response is GOOD or BAD.
    - GOOD → if it correctly and confidently answers the question.
    - BAD → if it's incomplete, uncertain, or irrelevant.

    Reply with only one word: GOOD or BAD.
    """

    result = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": evaluation_prompt}],
    )

    verdict = result.choices[0].message.content.strip().upper()
    print("AI verdict:", verdict)

    if "GOOD" in verdict:
        state["is_good"] = True
        return "endnode"
    else:
        state["is_good"] = False
        return "chatbot_gemini"


def chatbot_gemini(state: State):
    print("chatbot_gemini Node", state)
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            { "role": "user", "content": state.get("user_query") }
        ]
    )

    state["llm_output"] = response.choices[0].message.content
    return state

def endnode(state: State):
    print("endnode Node", state)
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chatbot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)


graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)

graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"user_query": "Hey, What is square root of -1?"}))
print(updated_state)