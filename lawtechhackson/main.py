from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from lawtechhackson.cos_lawyer import AIService
from lawtechhackson.lawyer_service import LawyerService

app = FastAPI()
ai_service = AIService()
lawyer_service = LawyerService()


@app.on_event("startup")
async def startup_event():
    print("start to init module")
    ai_service.load_model()
    await lawyer_service.init_mongo_with_collections()
    print("after init module")


@app.get("/")
def read_root():
    return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


class UserQuestionItem(BaseModel):
    question: str


@app.post("/query-lawyer")
async def query_lawyer(item: UserQuestionItem):
    question = item.question
    str_list = question.split()
    lawyer_name_list = ai_service.predict(str_list)
    # lawyer_name_list
    laywer_profile_list = await lawyer_service.get_lawyers_profile(
        lawyer_name_list)
    return laywer_profile_list
