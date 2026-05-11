from typing import Any, Dict, Iterable, List, Mapping, Sequence, cast

import numpy as np
from models import Criterion, CriterionBody


DEFAULT_CRITERIA = [
    Criterion("ipk", weight=0.3, type="BENEFIT"),
    Criterion("semester", weight=0.2, type="COST"),
    Criterion("penghasilan_ortu", weight=0.2, type="COST"),
    Criterion("jumlah_tanggungan", weight=0.1, type="BENEFIT"),
    Criterion("keaktifan_organisasi", weight=0.1, type="BENEFIT"),
    Criterion("skor_prestasi", weight=0.1, type="BENEFIT"),
]

ORGANIZATION_SCORE = {
    "tidak aktif": 1,
    "kurang aktif": 2,
    "cukup aktif": 3,
    "aktif": 4,
    "sangat aktif": 5,
}

CriterionInput = Criterion | CriterionBody | Mapping[str, Any]


def hitung_topsis(
    mahasiswa_list: Iterable[Any],
    criteria_body: CriterionInput | Sequence[CriterionInput] | None = None,
) -> List[Dict[str, Any]]:
    return calculate_topsis(mahasiswa_list, criteria_body)


def calculate_topsis(
    mahasiswa_list: Iterable[Any],
    criteria_body: CriterionInput | Sequence[CriterionInput] | None = None,
) -> List[Dict[str, Any]]:
    data = list(mahasiswa_list)
    if not data:
        return []

    criteria = _build_criteria(criteria_body)
    weight_vector = _build_weight_vector(criteria)
    decision_matrix = np.array(
        [_build_criteria_values(mahasiswa, criteria) for mahasiswa in data],
        dtype=float,
    )

    divisors = np.linalg.norm(decision_matrix, axis=0)
    normalized_matrix = np.divide(
        decision_matrix,
        divisors,
        out=np.zeros_like(decision_matrix),
        where=divisors != 0,
    )
    weighted_matrix = normalized_matrix * weight_vector

    benefit_mask = np.array(
        [criterion.type == "BENEFIT" for criterion in criteria],
        dtype=bool,
    )
    max_values = weighted_matrix.max(axis=0)
    min_values = weighted_matrix.min(axis=0)
    ideal_positive = np.where(benefit_mask, max_values, min_values)
    ideal_negative = np.where(benefit_mask, min_values, max_values)

    positive_distances = np.linalg.norm(weighted_matrix - ideal_positive, axis=1)
    negative_distances = np.linalg.norm(weighted_matrix - ideal_negative, axis=1)
    total_distances = positive_distances + negative_distances
    preference_values = np.divide(
        negative_distances,
        total_distances,
        out=np.zeros_like(negative_distances),
        where=total_distances != 0,
    )

    results = []
    for mahasiswa, preference_value, positive_distance, negative_distance in zip(
        data,
        preference_values,
        positive_distances,
        negative_distances,
    ):
        results.append({
            "nama": _get_value(mahasiswa, "nama"),
            "unique_name": _get_value(mahasiswa, "unique_name"),
            "nilai_preferensi": round(float(preference_value), 6),
            "jarak_ideal_positif": round(float(positive_distance), 6),
            "jarak_ideal_negatif": round(float(negative_distance), 6),
            "kriteria": _build_original_values(mahasiswa, criteria),
        })

    results.sort(key=lambda item: item["nilai_preferensi"], reverse=True)
    for index, result in enumerate(results, start=1):
        result["ranking"] = index

    return results


def _build_criteria(
    criteria_body: CriterionInput | Sequence[CriterionInput] | None,
) -> List[Criterion]:
    if criteria_body is None:
        return list(DEFAULT_CRITERIA)

    if isinstance(criteria_body, Mapping) and "criteria" in criteria_body:
        criteria_body = criteria_body["criteria"]

    if isinstance(criteria_body, Sequence) and not isinstance(
        criteria_body,
        (str, bytes, bytearray),
    ):
        criteria = [_to_criterion(item) for item in criteria_body]
    else:
        criteria = [_to_criterion(cast(CriterionInput, criteria_body))]

    if not criteria:
        raise ValueError("Kriteria tidak boleh kosong")

    duplicate_names = _find_duplicate_names(criteria)
    if duplicate_names:
        raise ValueError(
            f"Kriteria duplikat: {', '.join(sorted(duplicate_names))}"
        )

    return criteria


def _to_criterion(item: CriterionInput) -> Criterion:
    name = _get_value(item, "name")
    weight = _get_value(item, "weight")
    criterion_type = _get_value(item, "type")

    if not name:
        raise ValueError("Nama kriteria wajib diisi")

    if criterion_type is None:
        raise ValueError(f"Tipe benefit/cost untuk {name} wajib diisi")

    return Criterion(
        name=str(name),
        weight=_to_float(weight, str(name)),
        type=_normalize_type(criterion_type, str(name)),
    )


def _build_weight_vector(criteria: Sequence[Criterion]) -> np.ndarray:
    weight_vector = np.array(
        [_to_float(criterion.weight, criterion.name) for criterion in criteria],
        dtype=float,
    )
    total_weight = weight_vector.sum()

    if total_weight <= 0:
        raise ValueError("Total bobot harus lebih besar dari 0")

    return weight_vector / total_weight


def _build_criteria_values(
    mahasiswa: Any,
    criteria: Sequence[Criterion],
) -> List[float]:
    return [
        _field_to_float(_get_value(mahasiswa, criterion.name), criterion.name)
        for criterion in criteria
    ]


def _build_original_values(
    mahasiswa: Any,
    criteria: Sequence[Criterion],
) -> Dict[str, Any]:
    return {
        criterion.name: _get_value(mahasiswa, criterion.name)
        for criterion in criteria
    }


def _field_to_float(value: Any, field: str) -> float:
    if field == "keaktifan_organisasi":
        return _organization_to_score(value)

    return _to_float(value, field)


def _organization_to_score(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    normalized_value = str(value or "").strip().lower()
    if normalized_value in ORGANIZATION_SCORE:
        return float(ORGANIZATION_SCORE[normalized_value])

    try:
        return float(normalized_value.replace(",", "."))
    except ValueError as exc:
        raise ValueError(
            "Nilai keaktifan_organisasi harus berupa angka atau salah satu dari: "
            f"{', '.join(ORGANIZATION_SCORE)}"
        ) from exc


def _find_duplicate_names(criteria: Sequence[Criterion]) -> set[str]:
    seen = set()
    duplicates = set()

    for criterion in criteria:
        if criterion.name in seen:
            duplicates.add(criterion.name)
        seen.add(criterion.name)

    return duplicates


def _get_value(source: Any, field: str) -> Any:
    if isinstance(source, Mapping):
        return source.get(field)

    return getattr(source, field, None)


def _to_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Nilai {field} harus berupa angka") from exc


def _normalize_type(value: Any, field: str) -> str:
    normalized_value = str(value).strip().upper()
    if normalized_value in {"BENEFIT", "COST"}:
        return normalized_value

    raise ValueError(f"Tipe kriteria untuk {field} harus BENEFIT atau COST")
