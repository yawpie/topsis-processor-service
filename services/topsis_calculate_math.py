import math
from typing import Any, Dict, Iterable, List, Mapping, Optional


CRITERIA = {
    "ipk": "benefit",
    "semester": "cost",
    "penghasilan_ortu": "cost",
    "jumlah_tanggungan": "benefit",
    "keaktifan_organisasi": "benefit",
    "skor_prestasi": "benefit",
}

DEFAULT_WEIGHTS = {criterion: 1 for criterion in CRITERIA}

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

    normalized_weights = _normalize_weights(weights or DEFAULT_WEIGHTS)
    matrix = [_build_criteria_values(mahasiswa) for mahasiswa in data]

    divisors = []
    for criterion in CRITERIA:
        divisor = math.sqrt(sum(row[criterion] ** 2 for row in matrix))
        divisors.append((criterion, divisor))

    weighted_matrix = []
    for row in matrix:
        weighted_row = {}
        for criterion, divisor in divisors:
            normalized_value = row[criterion] / divisor if divisor else 0
            weighted_row[criterion] = normalized_value * normalized_weights[criterion]
        weighted_matrix.append(weighted_row)

    ideal_positive = {}
    ideal_negative = {}
    for criterion, criterion_type in CRITERIA.items():
        values = [row[criterion] for row in weighted_matrix]

        if criterion_type == "benefit":
            ideal_positive[criterion] = max(values)
            ideal_negative[criterion] = min(values)
        else:
            ideal_positive[criterion] = min(values)
            ideal_negative[criterion] = max(values)

    results = []
    for mahasiswa, row in zip(data, weighted_matrix):
        positive_distance = _euclidean_distance(row, ideal_positive)
        negative_distance = _euclidean_distance(row, ideal_negative)
        total_distance = positive_distance + negative_distance
        preference_value = negative_distance / total_distance if total_distance else 0

        results.append({
            # "id": _get_value(mahasiswa, "id"),
            "nama": _get_value(mahasiswa, "nama"),
            "unique_name": _get_value(mahasiswa, "unique_name"), # todo hapus kalau sudah ada fix yang lebih baik
            "nilai_preferensi": round(preference_value, 6),
            "jarak_ideal_positif": round(positive_distance, 6),
            "jarak_ideal_negatif": round(negative_distance, 6),
            "kriteria": _build_original_values(mahasiswa),
        })

    results.sort(key=lambda item: item["nilai_preferensi"], reverse=True)
    for index, result in enumerate(results, start=1):
        result["ranking"] = index

    return results


def hitung_topsis(
    mahasiswa_list: Iterable[Any],
    weights: Optional[Mapping[str, float]] = None,
) -> List[Dict[str, Any]]:
    return calculate_topsis(mahasiswa_list, weights)


def _normalize_weights(weights: Mapping[str, float]) -> Dict[str, float]:
    missing_criteria = set(CRITERIA) - set(weights)
    if missing_criteria:
        raise ValueError(f"Bobot belum lengkap untuk kriteria: {', '.join(sorted(missing_criteria))}")

    normalized_weights = {criterion: _to_float(weights[criterion], criterion) for criterion in CRITERIA}
    total_weight = sum(normalized_weights.values())

    if total_weight <= 0:
        raise ValueError("Total bobot harus lebih besar dari 0")

    return {
        criterion: weight / total_weight
        for criterion, weight in normalized_weights.items()
    }


def _build_criteria_values(mahasiswa: Any) -> Dict[str, float]:
    return {
        "ipk": _to_float(_get_value(mahasiswa, "ipk"), "ipk"),
        "semester": _to_float(_get_value(mahasiswa, "semester"), "semester"),
        "penghasilan_ortu": _to_float(_get_value(mahasiswa, "penghasilan_ortu"), "penghasilan_ortu"),
        "jumlah_tanggungan": _to_float(_get_value(mahasiswa, "jumlah_tanggungan"), "jumlah_tanggungan"),
        "keaktifan_organisasi": _organization_to_score(_get_value(mahasiswa, "keaktifan_organisasi")),
        "skor_prestasi": _to_float(_get_value(mahasiswa, "skor_prestasi"), "skor_prestasi"),
    }


def _build_original_values(mahasiswa: Any) -> Dict[str, Any]:
    return {
        criterion: _get_value(mahasiswa, criterion)
        for criterion in CRITERIA
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


def _euclidean_distance(row: Mapping[str, float], ideal: Mapping[str, float]) -> float:
    return math.sqrt(
        sum((row[criterion] - ideal[criterion]) ** 2 for criterion in CRITERIA)
    )


def _get_value(source: Any, field: str) -> Any:
    if isinstance(source, Mapping):
        return source.get(field)

    return getattr(source, field, None)


def _to_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Nilai {field} harus berupa angka") from exc