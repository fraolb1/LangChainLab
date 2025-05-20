from fastapi import APIRouter
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter()

tagging_prompt = ChatPromptTemplate.from_template(
  """
  Extract the desired information from the following passage.
  only extract properties that are defined in the 'Classification' function.
  
  passage:
  {input}
  """
)

class Classification(BaseModel):
  sentiment:str = Field(description="rates the sentiment of the passage from 1 to 10 and also describe it. 1 being the least.")
  aggressiveness:str = Field(description="describes whether the passage is aggressive or not and rate the aggressiveness.")
  language:str = Field(description="The language in which the passage is written.")
  english_translation: str = Field(description="Translation of the passage into english if not already in english.")


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
structured_llm = llm.with_structured_output(Classification)

class Request_Body(BaseModel):
  input:str
  
@router.post('/')
def classify(body:Request_Body):
  input = body.input
  response = structured_llm.invoke(input)
  return response.model_dump()