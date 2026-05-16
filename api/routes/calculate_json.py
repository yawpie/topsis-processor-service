from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import hitung_topsis_dynamic
from models import CriterionBody

router = APIRouter()


class AlternativeItem(BaseModel):
    nama: str
    kode_alternatif: str | None = None
    metadata: str | None = None
    kriteria: dict[str, Any]


class CalculateJsonRequest(BaseModel):
    alternatives: list[AlternativeItem]
    criteria: list[CriterionBody]


@router.post("/calculate-json")
async def calculate_json(body: CalculateJsonRequest):
    if not body.alternatives:
        raise HTTPException(status_code=400, detail="Alternatives tidak boleh kosong")

    if not body.criteria:
        raise HTTPException(status_code=400, detail="Criteria tidak boleh kosong")

    # Flatten alternatives: merge kriteria values into the top-level dict
    # so hitung_topsis_dynamic can access them by criterion name
    data = []
    for alt in body.alternatives:
        item: dict[str, Any] = {
            "nama": alt.nama,
            "kode_alternatif": alt.kode_alternatif,
            "metadata": alt.metadata,
            **alt.kriteria,
        }
        data.append(item)

    result = hitung_topsis_dynamic(data, body.criteria)

    return {
        "message": "Perhitungan berhasil",
        "data": result,
    }
