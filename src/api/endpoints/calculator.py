from langchain.chat_models import init_chat_model
from fastapi import APIRouter
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv
from typing import TypedDict, Literal, Union
from pydantic import BaseModel

load_dotenv()
router = APIRouter()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai", google_api_key=os.getenv("GOOGLE_API_KEY"))

class State(TypedDict):
  question:str
  next:Literal["check", "tool", "final"]
  answer: Union[str, None]
  numbers: Union[list[float], None]

class Body(BaseModel):
  question:str


def check_if_math(state:State) -> State:
  q = state["question"]
  system_prompt = "You are a router. say 'math' if the question is about math or say 'text' otherwise."
  result = model.invoke([{"role":"system", "content":system_prompt},
                {"role":"user", "content":q}])
  
  route = result.content.strip()
  
  if route == "math":
    numbers = [float(s) for s in q.split() if s.isdigit()]
    return {"question":q, "numbers":numbers, "next":"tool","answer":None}
  else:
    return {"question":q, "numbers":None, "next":'final', "answer":None}

def calculator(state:State) -> State:
  numbers = state["numbers"]
  total = sum(numbers)
  return {"question": state["question"], "numbers": numbers, "answer": total, "next": "final"}

def final_answer(state:State) -> State:
  if state["answer"]:
    return state
  llm_answer = model.invoke(state["question"])
  answer = llm_answer.content
  return {**state, "answer":answer}

builder = StateGraph(state_schema=State)

builder.add_node("check", check_if_math)
builder.add_node('tool', calculator)
builder.add_node('final', final_answer)

builder.set_entry_point("check")

builder.add_conditional_edges("check", lambda state: state["next"],{
  "tool":"tool",
  "final":"final"
})

builder.add_edge("tool", "final")
builder.set_finish_point("final")

config = {"configurable": {"thread_id": "abc123"}}
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

@router.post('/')
def chat(body:Body):
  question = body.question
  result = graph.invoke({"question": question, "next": "check", "answer": None, "numbers": None}, config)
  
  return result["answer"]