from typing import Union
from fastapi import FastAPI ,Depends

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker , Session
from sqlalchemy import Column , Integer , String
from pydantic import BaseModel
from fastapi import Request

# Step 1 : Create SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Step 2 : ORM Class
class ItemDB(Base):
    __tablename__='Item'
    id=Column(Integer,primary_key=True)
    title=Column(String,index=True)
    description=Column(String,index=True)
    price=Column(Integer,index=True)

#Sync Schema -> สร้างฐานข้อมูล เทียบclass ORM กับ Database ถ้าตัวไหนหายไปจะได้สร้างรองรับไว้ก่อน
Base.metadata.create_all(bind=engine)

app =FastAPI()

#Step 3 : Pydantic Model

#1Base
class ItemBase(BaseModel):
    title:str
    description : str
    price : float

#2Request
class ItemCreate(ItemBase):
    pass

#3Response
class ItemResponse(ItemBase):
    id : int
    class Config:
        from_attributes= True

#4Dependency กำหนด Session ของ DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#---------------------------------------------------------------------------

@app.post('/items',response_model=ItemResponse)
def create_item(item:ItemBase,db:Session= Depends(get_db)):
    # db_item=Item(title=item.title,description=item.description,price=item.price) อันนี้เป็นการadd ราย field
    #อันล่างจะเป็นการ add ทั้งหมด
    db_item= ItemDB(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


#เป็นตัวset path หลังจากlocalhost ; 127.0.0.1:8000/บลาๆๆ ตามที่เราset pathไว้เลย
# @app.get("/")
# def say():
#     return{'message':'Hello ,Who are you ?'}

# @app.get("/player/{id}")
# def read_id(id: int):
#     return {"player":f'Hello player {id}' }

# รับค่าrequest เข้ามาmapกับรูปแบบ jason แล้วแสดงผล
# Feed pydantic model to function to maping

# Define Object โดยใช้ Pydantic lib.
# from pydantic import BaseModel
# class Item(BaseModel):
#     name:str
#     price: float

# #q-> querystring it's optional to do 
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

# @app.put('/items/{item_id}')
# def edit_item(item_id:int,item:Item):
#     return{'id':item_id , 'request body':item}

# @app.delete('/items/{item_id}')
# def delete_item(item_id:int,item:Item):
#     return{'id':item_id , 'request body':item}