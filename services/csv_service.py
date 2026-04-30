import pandas as pd
from io import StringIO


def parse_csv(content: bytes):
    # df = pd.read_csv(StringIO(content.decode("utf-8")))
    df = pd.read_csv(StringIO(content.decode("utf-8-sig")), sep=";")
    print(df.head())
    # normalisasi kolom
    df.columns = df.columns.str.strip().str.lower()

    data_list = []

    for _, row in df.iterrows():
        data_list.append({
            "nama": row["nama"],
            "ipk": float(row["ipk"]),
            "semester": int(row["semester"]),
            "penghasilan_ortu": int(row["penghasilan_ortu"]),
            "jumlah_tanggungan": int(row["jumlah_tanggungan"]),
            "keaktifan_organisasi": row["keaktifan_organisasi"],
            "skor_prestasi": float(row["skor_prestasi"])
        })

    return data_list
