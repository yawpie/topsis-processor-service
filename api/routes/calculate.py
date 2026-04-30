from fastapi import APIRouter, UploadFile, File
from services.csv_service import parse_csv
from services import hitung_topsis_numpy, hitung_topsis_math
router = APIRouter()


@router.post("/calculate-np")
async def calculate_numpy(file: UploadFile = File(...)):
    content = await file.read()

    data = parse_csv(content)
    result = hitung_topsis_numpy(data)
    

    return {
        "message": "Upload berhasil",
        "data": result
    }


@router.post("/calculate-math")
async def calculate_math(file: UploadFile = File(...)):
    content = await file.read()

    data = parse_csv(content)
    result = hitung_topsis_math(data)

    return {
        "message": "Upload berhasil",
        "data": result
    }
