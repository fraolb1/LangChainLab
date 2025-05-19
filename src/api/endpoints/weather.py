from fastapi import APIRouter
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

load_dotenv()

BASE_URL = "http://api.weatherapi.com/v1/current.json"

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai", google_api_key=os.getenv("GOOGLE_API_KEY"))




router = APIRouter()

class WeatherApiCallInput(BaseModel):
  city:str = Field(description="the city to get weather from")

@tool("get_weather_from_api", args_schema=WeatherApiCallInput)
def get_weather_from_api(city:str="london"):
  """Get weather of a city"""
  weatherApiKey = os.getenv("WEATHER_API_KEY")
  params = {
    "key": weatherApiKey,
    "q":city
  }
  response = requests.get(BASE_URL, params)
  return response.json()
  
model_With_tool = model.bind_tools([get_weather_from_api])


messages = [
  SystemMessage("You are a weather assistant. Use available tools to help the user."),
]

@router.get("/")
def get_weather(city: str = "paris"):
    messages = [HumanMessage(content=f"What is the weather in {city} currently")]

    response = model_With_tool.invoke(messages)

    tool_calls = response.tool_calls

    tool_responses = []
    for tool_call in tool_calls:
        tool_name = tool_call["name"].lower()
        if tool_name not in {"get_weather_from_api"}:
            raise ValueError(f"Unknown tool: {tool_name}")
        selected_tool = {"get_weather_from_api": get_weather_from_api}[tool_name]

        tool_output = selected_tool.invoke(tool_call)
        tool_responses.append(
            ToolMessage(content=tool_output, tool_call_id=tool_call["id"])
        )

    messages.append(response)  
    messages.extend(tool_responses)

    final_res = model_With_tool.invoke(messages)

    return {"response": final_res.content}
