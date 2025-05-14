from fastapi import APIRouter
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import chain


router = APIRouter()

filepath = "src\docs\document.pdf"
loader = PyPDFLoader(file_path=filepath)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
all_splits = text_splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="src/chroma_langchain_db", 
)

vector_store.add_documents(documents=all_splits)

results = vector_store.similarity_search(
    "what is compiler?"
)

@chain
def retriever(query):
  return vector_store.similarity_search(query, k=1)

batch_retrieve = retriever.batch([ "what is compiler?", "why steps are there in compiler?"])


@router.get('/search')
def getDocLen():
  return len(all_splits), batch_retrieve

