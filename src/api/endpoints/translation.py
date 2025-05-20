from fastapi import APIRouter
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai", google_api_key=os.getenv("GOOGLE_API_KEY"))


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


@tool("multiplication-tool", args_schema=CalculatorInput)
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
model_with_tool = model.bind_tools([multiply])


messages = [
  SystemMessage("You are a mathematician assistant."),
  HumanMessage('what is 2 times 3.'),
  AIMessage('2 times 3 equals 6.'),
  HumanMessage("how come?")
]

system_template = "Translate the following from English into {language}"

prompt_template = ChatPromptTemplate.from_messages(
  [("system", system_template),("user", "{text}")]
)

prompt = prompt_template.invoke({"language":"Amharic", "text":"Good Night"}).to_messages()

@router.get('/')
def getMessage():
  response = model.invoke(prompt)
  return response