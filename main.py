from fastapi import FastAPI
from api.routes import index_router

app = FastAPI()

# register router
app.include_router(index_router)
