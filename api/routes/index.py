from fastapi import APIRouter
from .upload import router as upload_router
from .calculate import router as calculate_router
from .calculate_json import router as calculate_json_router

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Welcome to TOPSIS Processor API"}


router.include_router(calculate_router)
router.include_router(calculate_json_router)

router.include_router(upload_router)
