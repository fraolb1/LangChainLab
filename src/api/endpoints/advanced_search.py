from fastapi import APIRouter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain import hub
from langgraph.graph import StateGraph, START
import bs4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import TypedDict, List, Union
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
router = APIRouter()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai", google_api_key=os.getenv("GOOGLE_API_KEY"))

loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)

class State(TypedDict):
  question: str
  context: Union[List[Document], None]
  answer: Union[str, None]

docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

splitted_doc = splitter.split_documents(docs)

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_store = Chroma(
  collection_name="advanced_searching",
  embedding_function=embedding
)

vector_store.add_documents(splitted_doc)

prompt = hub.pull("rlm/rag-prompt", api_url="https://api.smith.langchain.com")

def retrieve(state:State) :
  retrieved_docs = vector_store.similarity_search(state["question"])
  return {**state, "context":retrieved_docs}

def generate(state:State):
  docs_content = "\n\n".join(doc.page_content for doc in state["context"])
  messages = prompt.invoke({'question':state['question'], 'context':docs_content})
  result = model.invoke(messages)
  return {**state, 'answer':result.content}


graph_builder = StateGraph(state_schema=State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

class Body(BaseModel):
  question:str

@router.post('/')
def search(body:Body):
  question = body.question
  response = graph.invoke({"question": question, "context": None, "answer": None})
  return response["answer"]