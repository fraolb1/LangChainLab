from fastapi import APIRouter
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import BaseModel
from langchain_core.runnables import chain

router = APIRouter()

class SearchInput(BaseModel):
  question: list[str]

filepath = "src\docs\document.pdf"
loader = PyPDFLoader(filepath)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)

all_split = splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_store = Chroma(
  collection_name="example_collection",
  embedding_function=embeddings,
  # persist_directory="src/another_chroma"
)

vector_store.add_documents(documents=all_split)

@chain
def retriever(query):
  return vector_store.similarity_search(query, k=1)

@router.post('/')
def search(search:SearchInput):
  questions = search.question
  
  result = retriever.batch(questions)
  
  return {"question":questions,"result" : result}
