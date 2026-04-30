from fastapi import FastAPI
from api.routes import index_router
from core.database import Base, engine

app = FastAPI()

# create table
Base.metadata.create_all(bind=engine)

# register router
app.include_router(index_router)