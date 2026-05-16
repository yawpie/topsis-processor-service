import csv
import re

import pandas as pd
from io import StringIO


IDENTIFIER_COLUMNS = (
    "kode_alternatif",
    "nama",
    "name",
    "alternatif",
    "id",
    "kode",
    "student",
    "mahasiswa",
)


def parse_float(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = value.replace(",", ".")

    return float(value)


def parse_int(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = value.replace(".", "")  # jaga-jaga kalau ada format 1.500.000

    return int(value)

def parse_csv(content: bytes):
    csv_text = content.decode("utf-8-sig")
    delimiter = _detect_delimiter(csv_text)
    df = pd.read_csv(
        StringIO(csv_text),
        sep=delimiter,
        dtype=str,
        keep_default_na=False,
    )

    df.columns = _deduplicate_columns([
        _normalize_column_name(column)
        for column in df.columns
    ])

    identifier_column = _find_identifier_column(df.columns)

    data_list = []

    for _, row in df.iterrows():
        parsed_row = {
            column: _parse_value(row[column])
            for column in df.columns
        }
        parsed_row["kode_alternatif"] = _parse_identifier(row[identifier_column])
        data_list.append(parsed_row)

    return data_list


def _detect_delimiter(csv_text: str) -> str:
    sample = csv_text[:4096]

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,\t|")
        return dialect.delimiter
    except csv.Error:
        first_line = next(
            (line for line in csv_text.splitlines() if line.strip()),
            "",
        )
        delimiter_counts = {
            delimiter: first_line.count(delimiter)
            for delimiter in (";", ",", "\t", "|")
        }
        return max(delimiter_counts, key=lambda delimiter: delimiter_counts[delimiter])


def _normalize_column_name(column: str) -> str:
    normalized = str(column).strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")

    return normalized or "column"


def _deduplicate_columns(columns: list[str]) -> list[str]:
    seen = {}
    deduplicated_columns = []

    for column in columns:
        count = seen.get(column, 0)
        seen[column] = count + 1

        if count == 0:
            deduplicated_columns.append(column)
        else:
            deduplicated_columns.append(f"{column}_{count + 1}")

    return deduplicated_columns


def _find_identifier_column(columns) -> str:
    columns = list(columns)

    matches = [
        candidate
        for candidate in IDENTIFIER_COLUMNS
        if candidate in columns
    ]

    if len(matches) > 1:
        raise ValueError(
            f"CSV memiliki lebih dari satu kolom identifier: {', '.join(matches)}. "
            f"Harap gunakan hanya satu kolom identifier dari: {', '.join(IDENTIFIER_COLUMNS)}. "
            f"Kolom identifier lainnya harus dihapus atau diganti namanya."
        )

    if len(matches) == 1:
        return matches[0]

    return columns[0]


def _parse_value(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    if text == "":
        return None

    numeric_value = _parse_number(text)
    if numeric_value is not None:
        return numeric_value

    return text


def _parse_identifier(value) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text or None


def _parse_number(text: str):
    if not re.fullmatch(r"[+-]?\d[\d., ]*", text):
        return None

    normalized = text.replace(" ", "")
    has_comma = "," in normalized
    has_dot = "." in normalized

    if has_comma and has_dot:
        decimal_separator = "," if normalized.rfind(",") > normalized.rfind(".") else "."
        thousands_separator = "." if decimal_separator == "," else ","
        normalized = normalized.replace(thousands_separator, "")
        normalized = normalized.replace(decimal_separator, ".")
    elif has_comma:
        normalized = _normalize_single_separator_number(normalized, ",")
    elif has_dot:
        normalized = _normalize_single_separator_number(normalized, ".")

    try:
        number = float(normalized)
    except ValueError:
        return None

    if number.is_integer() and "." not in normalized:
        return int(number)

    return number


def _normalize_single_separator_number(text: str, separator: str) -> str:
    separator_count = text.count(separator)
    integer_part, decimal_part = text.rsplit(separator, 1)

    if separator_count > 1:
        return text.replace(separator, "")

    if len(decimal_part) == 3 and len(integer_part.lstrip("+-")) > 1:
        return text.replace(separator, "")

    if separator == ",":
        return text.replace(",", ".")

    return text
