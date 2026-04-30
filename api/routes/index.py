from .upload import router as upload_router
from fastapi import APIRouter

router = APIRouter()
@router.get("/")
def read_root():
    return {"message": "Welcome to TOPSIS Processor API"}

router.include_router(upload_router)