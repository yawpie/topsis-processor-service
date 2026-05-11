from typing import Any, Dict, Iterable, List, Mapping, Optional
from models import Criterion
import numpy as np


# CRITERIA = {
#     "ipk": "benefit",
#     "semester": "cost",
#     "penghasilan_ortu": "cost",
#     "jumlah_tanggungan": "benefit",
#     "keaktifan_organisasi": "benefit",
#     "skor_prestasi": "benefit",
# }

CRITERIA_MODELS = [
    Criterion("ipk", weight=0.3, is_benefit=True),
    Criterion("semester", weight=0.2, is_benefit=False),
    Criterion("penghasilan_ortu", weight=0.2, is_benefit=False),
    Criterion("jumlah_tanggungan", weight=0.1, is_benefit=True),
    Criterion("keaktifan_organisasi", weight=0.1, is_benefit=True),
    Criterion("skor_prestasi", weight=0.1, is_benefit=True),
]

# DEFAULT_WEIGHTS = {criterion: 1 for criterion in CRITERIA}
DEFAULT_WEIGHTS = {
    "ipk": 0.3,
    "semester": 0.2,
    "penghasilan_ortu": 0.2,
    "jumlah_tanggungan": 0.1,
    "keaktifan_organisasi": 0.1,
    "skor_prestasi": 0.1,
}

ORGANIZATION_SCORE = {
    "tidak aktif": 1,
    "kurang aktif": 2,
    "cukup aktif": 3,
    "aktif": 4,
    "sangat aktif": 5,
}


def calculate_topsis(
    mahasiswa_list: Iterable[Any],
    weights: Optional[Mapping[str, float]] = None,
) -> List[Dict[str, Any]]:
    data = list(mahasiswa_list)
    if not data:
        return []

    criteria_names = tuple(criterion.name for criterion in CRITERIA_MODELS)
    weight_vector = _normalize_weights(weights or DEFAULT_WEIGHTS)
    decision_matrix = np.array(
        [_build_criteria_values(mahasiswa) for mahasiswa in data],
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
        [criterion.is_benefit for criterion in CRITERIA_MODELS]
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
            # "id": _get_value(mahasiswa, "id"),
            "nama": _get_value(mahasiswa, "nama"),
            "unique_name": _get_value(mahasiswa, "unique_name"), # todo hapus kalau sudah ada fix yang lebih baik
            "nilai_preferensi": round(float(preference_value), 6),
            "jarak_ideal_positif": round(float(positive_distance), 6),
            "jarak_ideal_negatif": round(float(negative_distance), 6),
            "kriteria": _build_original_values(mahasiswa),
        })

    results.sort(key=lambda item: item["nilai_preferensi"], reverse=True)
    for index, result in enumerate(results, start=1):
        result["ranking"] = index

    return results


def hitung_topsis(
    mahasiswa_list: Iterable[Any],
    weights: Optional[Mapping[str, float]] = None,
    criterion_models: Optional[List[Criterion]] = None,
) -> List[Dict[str, Any]]:
    return calculate_topsis(mahasiswa_list, weights)


def _normalize_weights(weights: Mapping[str, float]) -> np.ndarray:
    missing_criteria = set(criterion.name for criterion in CRITERIA_MODELS) - set(weights)
    if missing_criteria:
        raise ValueError(
            f"Bobot belum lengkap untuk kriteria: {', '.join(sorted(missing_criteria))}"
        )

    weight_vector = np.array(
        [_to_float(weights[criterion.name], criterion.name) for criterion in CRITERIA_MODELS],
        dtype=float,
    )
    total_weight = weight_vector.sum()

    if total_weight <= 0:
        raise ValueError("Total bobot harus lebih besar dari 0")

    return weight_vector / total_weight


def _build_criteria_values(mahasiswa: Any) -> List[float]:
    return [
        _to_float(_get_value(mahasiswa, criterion.name), criterion.name)
        for criterion in CRITERIA_MODELS
    ]


def _build_original_values(mahasiswa: Any) -> Dict[str, Any]:
    return {
        criterion.name: _get_value(mahasiswa, criterion.name)
        for criterion in CRITERIA_MODELS
    }


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


def _get_value(source: Any, field: str) -> Any:
    if isinstance(source, Mapping):
        return source.get(field)

    return getattr(source, field, None)


def _to_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Nilai {field} harus berupa angka") from exc
