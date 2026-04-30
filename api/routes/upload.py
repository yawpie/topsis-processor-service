from fastapi import APIRouter, UploadFile, File
from services.csv_service import parse_csv

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()

    data = parse_csv(content)

    return {
        "message": "Upload berhasil",
        "data": data
    }