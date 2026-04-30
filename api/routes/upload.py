from fastapi import APIRouter, UploadFile, File
from core.database import SessionLocal
from services.csv_service import parse_csv
from repositories.mahasiswa_repo import bulk_insert_mahasiswa

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()

    data = parse_csv(content)

    db = SessionLocal()
    bulk_insert_mahasiswa(db, data)
    db.close()

    return {
        "message": "Upload berhasil",
        "total": len(data)
    }