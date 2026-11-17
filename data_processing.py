from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = [
    "Lokasi", "Bagian", "Kode Asset", "Kategori", "Nama Barang",
    "Fungsi / Tipe", "Merk", "Ukuran / Spesifikasi", "Warna", "Bahan",
    "Tahun Pembelian", "Jumlah", "Kondisi", "Status", "Penanggung Jawab (PIC)",
    "Aset_Bermasalah"
]

def load_inventory(path):
    path = Path(path)
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype={"Kode Asset": "string"})
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing}")
    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)
    df["Aset_Bermasalah"] = pd.to_numeric(df["Aset_Bermasalah"], errors="coerce").fillna(0).astype(int)
    for col in df.columns:
        if col not in ["Jumlah", "Aset_Bermasalah"]:
            df[col] = df[col].astype("string").fillna("").str.strip()
    return df

def apply_filters(df, bagian="Semua", lokasi="Semua", kategori="Semua", kondisi="Semua"):
    result = df.copy()
    for col, value in [("Bagian", bagian), ("Lokasi", lokasi), ("Kategori", kategori), ("Kondisi", kondisi)]:
        if value != "Semua":
            result = result[result[col] == value]
    return result
