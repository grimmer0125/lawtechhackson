# TODO:
# 使用 https://github.com/ets-labs/python-dependency-injector
# 1. 初始化 DB / AI
#   1. singleton
#   2. or resource https://python-dependency-injector.ets-labs.org/providers/resource.html
# 2. 跟 fastapi 整合
#   1. https://python-dependency-injector.ets-labs.org/examples/fastapi.html#fastapi-example
#   2. https://python-dependency-injector.ets-labs.org/examples/fastapi-redis.html#fastapi-redis-example
#   3. https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.html
# 3. 多個/層 containers  https://github.com/ets-labs/python-dependency-injector
#  1. Containers. Provides declarative and dynamic containers. See Containers.

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from lawtechhackson.cos_lawyer import AIService
from lawtechhackson.lawyer_service import LawyerProfile, LawyerService
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # FIXME: 加了 fastapi response_model 會 error
    # response_model=list[LawyerProfile]): TypeError: Object of type 'type' is not JSON serializable
    question = item.question
    str_list = question.split()
    lawyer_name_list = ai_service.predict(str_list)
    # lawyer_name_list
    laywer_profile_list = await lawyer_service.get_lawyers_profile(
        lawyer_name_list)
    return laywer_profile_list


from typing import Any, Optional


class LawyerDetailQueryItem(BaseModel):
    lawyer_name: str
    # now_lic_no: Optional[str]


@app.post("/lawyer-detail")
async def lawyer_detail(item: LawyerDetailQueryItem):
    lawyer_name = item.lawyer_name
    judgment_list = await lawyer_service.get_lawyer_detail_profile(lawyer_name)
    return judgment_list
