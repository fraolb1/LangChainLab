from typing import Union
from fastapi import FastAPI
from src.api.routes import api_router

app = FastAPI()
app.include_router(api_router, prefix="/api")

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}