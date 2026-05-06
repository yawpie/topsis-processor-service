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

def create_unique_name(original_name: str) -> str:
    timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
    random_suffix = pd.util.hash_pandas_object(pd.Series([original_name])).iloc[0] % 100000
    extension = original_name[original_name.rfind("."):] if "." in original_name else ""
    clean_name = original_name[:original_name.rfind(".")] if "." in original_name else original_name
    clean_name = clean_name.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
    return f"{clean_name}_{timestamp}_{random_suffix}{extension}"

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
            "unique_name": create_unique_name(str(row["nama"])),
            "ipk": parse_float(row["ipk"]),
            "semester": parse_int(row["semester"]),
            "penghasilan_ortu": parse_int(row["penghasilan_ortu"]),
            "jumlah_tanggungan": parse_int(row["jumlah_tanggungan"]),
            "keaktifan_organisasi": str(row["keaktifan_organisasi"]).strip(),
            "skor_prestasi": parse_float(row["skor_prestasi"]),
        })

    return data_list