import pandas as pd
from io import StringIO


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
    df = pd.read_csv(
        StringIO(content.decode("utf-8-sig")),
        sep=";"
    )

    # Normalisasi nama kolom
    df.columns = df.columns.str.strip().str.lower()

    data_list = []

    for _, row in df.iterrows():
        data_list.append({
            "nama": str(row["nama"]).strip(),
            "ipk": parse_float(row["ipk"]),
            "semester": parse_int(row["semester"]),
            "penghasilan_ortu": parse_int(row["penghasilan_ortu"]),
            "jumlah_tanggungan": parse_int(row["jumlah_tanggungan"]),
            "keaktifan_organisasi": str(row["keaktifan_organisasi"]).strip(),
            "skor_prestasi": parse_float(row["skor_prestasi"]),
        })

    return data_list