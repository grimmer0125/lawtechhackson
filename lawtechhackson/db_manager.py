from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed, init_beanie
import asyncio, motor


class Category(BaseModel):
    """ demo """
    name: str
    description: str


class Product(Document):
    """ demo """
    name: str  # You can use normal types just like in pydantic
    description: Optional[str] = None
    price: Indexed(
        float
    )  # You can also specify that a field should correspond to an index
    category: Category  # You can include pydantic models as well


# class Car(Document):
#     name: Optional[str] = ""


# Beanie is fully asynchronous, so we will access it from an async function
async def example():
    await init_mongo("db_name", [Product])

    chocolate = Category(
        name="Chocolate",
        description="A preparation of roasted and ground cacao seeds.")
    # Beanie documents work just like pydantic models
    tonybar = Product(name="Tony's", price=5.95, category=chocolate)
    # And can be inserted into the database
    await tonybar.insert()
    print("done")


# Beanie is fully asynchronous, so we will access it from an async function
async def init_mongo(connect_str, db_name, document_models):

    # Beanie uses Motor under the hood
    client = motor.motor_asyncio.AsyncIOMotorClient(connect_str)

    # Init beanie with the Product document class
    await init_beanie(database=client[db_name],
                      document_models=document_models)
    print("done")


if __name__ == "__main__":
    print("start")
    asyncio.run(example())
