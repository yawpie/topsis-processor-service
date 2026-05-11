import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import TypeAdapter, ValidationError
from services.csv_service import parse_csv
from services import hitung_topsis_numpy
from models import CriterionBody

router = APIRouter()


criterion_body_adapter = TypeAdapter(list[CriterionBody])


@router.post("/calculate")
async def calculate_numpy(
    criterionBody: str = Form(...),
    file: UploadFile = File(...),
):
    content = await file.read()

    criteria = _parse_criterion_body(criterionBody)
    data = parse_csv(content)
    result = hitung_topsis_numpy(data, criteria)

    return {
        "message": "Upload berhasil",
        "data": result
    }


def _parse_criterion_body(criterion_body: str) -> list[CriterionBody]:
    try:
        raw_criteria = json.loads(criterion_body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail="criterionBody harus berupa JSON valid",
        ) from exc

    try:
        if isinstance(raw_criteria, list):
            return criterion_body_adapter.validate_python(raw_criteria)

        return [CriterionBody.model_validate(raw_criteria)]
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        ) from exc


# @router.post("/calculate-math")
# async def calculate_math(file: UploadFile = File(...)):
#     content = await file.read()

#     data = parse_csv(content)
#     result = hitung_topsis_math(data)

#     return {
#         "message": "Upload berhasil",
#         "data": result
#     }
