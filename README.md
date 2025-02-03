# FastAPI
## Importance Element
1. FastAPI
2. Pydantic
3. DB
4. SQLAlchemy
5. ORM
## Theory behind & Key takeaway
1. Basic Using FastAPI
   1. Init : ` app =FastAPI()`
   2. Using : Many type to choose base on **CRUD**
   - put : Create token to database
   - get : Request token response
   - post : Update the database
   - delete : Delete token from database that have the same attribute

   ```@app.get("/")```
   ```@app.put('/items/{item_id}') ```
   ```@app.delete('/items/{item_id}')```
   ```@app.post('/items',response_model=ItemResponse)```

    3. หลัง ('/') เป็น path ที่ต้องการจะไปต่อของapi เพื่อแยก function การยิงได้ง่ายและเป็นระเบียบขึ้น สามารถใส่ {}เป็นการรับattribute ที่อยู่ใน{} ไปเป็น variable ในการเรียกใช้ในfunction นั้นต่อไป
    4. สามารถใส่ พวกตัวกรองทั้งหลาย เพื่อเป็นการ query add เข้าไปหลัง ? เช่น `localhost:8000/items/3?sorted_by=date`
    ```
    @app.get("/items/{item_id}")
    def read_item(item_id: int, q: Union[str, None] = None):
        return {"item_id": item_id, "q": q}
    ```
2. การใช้ร่วมกับ Database : path ที่ต้องเข้าใจ
    Pydantic -> ORM -> SQL
3. Pydantic :เราใช้เพื่อสร้าง class ต่างๆใน python มันจัดการกับ class ในหลายๆ library ได้ดีมาก เราใช้มันสร้างobject ที่ต้องการเก็บใน token เพื่อส่งAPI
   ```
   from pydantic import BaseModel
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
   ```
4. สร้าง SQL ขึ้นมา
   โดยURL นี้เป็นการสร้างไฟล์ที่folderที่อยู่ ชื่อไฟล์ว่า sql_app
   สร้างเป็น engine และสร้างตัวจัดการsession bind เข้ากับ engine เพื่อจัดการtoken session 
    ```
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    ```
5. ORM เป็นตัวแปลง/Mapping Pydantic class เข้ากับ SQL column
   มีการสร้างBase ที่เป็น libของ SQLAlchemyเพื่อใช้ในการแปลงtype โดยส่ง Baseเข้าไปใน ItemDB class เพื่อเอาไปใช้ในเส้น API ในการเก็บข้อมูล

   ```
   Base = declarative_base()
   class ItemDB(Base):
        __tablename__='Item'
        id=Column(Integer,primary_key=True)
        title=Column(String,index=True)
        description=Column(String,index=True)
        price=Column(Integer,index=True)
    Base.metadata.create_all(bind=engine)
   ```
   และที่สำคัญ ห้ามลืมคือการ createmetadata ที่bind engineไว้ ทำให้ ถ้า fieldไหนไม่มีใน pydantic object มันจะสร้าง initial ให้เองใน Database
6. เส้น API ตัวอย่างเช่น Post เป็นการ Create ค่าลงเก็บใน Database ;
    ```
    @app.post('/items',response_model=ItemResponse)
    def create_item(item:ItemBase,db:Session= Depends(get_db)):
        db_item= ItemDB(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    ```
- อันนี้คือเป็นการกำหนดว่า เราจะตอบกลับโดยใช้ responsemodelอะไร
- การใส่ parameter เข้าไปจะต้องรับเป็น Item pydantic และ DB ที่มีการใช้ Sessionจัดการ ในที่นี้ให้ขึ้นsessionกับ get_db และภายในfunction ตือถ้าได้รับ pydantic model จะให้แปลงและยัดลงdatabase
- นี่คือcodeในการจัดการsessionของการget_db
  ```
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
  ```