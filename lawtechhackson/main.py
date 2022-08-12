from typing import Union
from fastapi import FastAPI
from lawtechhackson.cos_lawyer import AIService

app = FastAPI()

ai_service = AIService()


@app.on_event("startup")
async def startup_event():
    print("start to init module")
    ai_service.load_model()
    print("after init module")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


from pydantic import BaseModel


class UserQuestionItem(BaseModel):
    question: str


@app.post("/query-lawyer")
def query_lawyer(item: UserQuestionItem):
    question = item.question
    str_list = question.split()
    lawyer_name_list = ai_service.predict(str_list)
    return lawyer_name_list
