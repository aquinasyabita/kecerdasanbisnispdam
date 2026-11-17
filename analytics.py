import pandas as pd

def get_kpis(df):
    total = df["Jumlah"].sum()
    active = df.loc[df["Status"].str.lower() == "aktif", "Jumlah"].sum()
    inactive = df.loc[df["Status"].str.lower() == "tidak aktif", "Jumlah"].sum()
    attention = df.loc[df["Aset_Bermasalah"].eq(1), "Jumlah"].sum()
    damaged = df.loc[df["Kondisi"].eq("Rusak"), "Jumlah"].sum()
    return {
        "total": total, "active": active, "inactive": inactive,
        "attention": attention, "damaged": damaged,
        "problem_rate": attention / total * 100 if total else 0
    }

def get_data_quality(df):
    quality_columns = [
        c for c in [
            "Kode Asset", "Lokasi", "Bagian", "Kategori", "Nama Barang",
            "Fungsi / Tipe", "Merk", "Ukuran / Spesifikasi", "Warna",
            "Bahan", "Tahun Pembelian", "Kondisi", "Status",
            "Penanggung Jawab (PIC)"
        ] if c in df.columns
    ]
    rows = []
    for col in quality_columns:
        values = df[col].astype("string").str.strip()
        missing = values.isna() | values.isin(["", "-"])
        rows.append({
            "Variabel": col,
            "Jumlah Kosong": int(missing.sum()),
            "Kelengkapan (%)": round((~missing).mean() * 100, 2),
            "Kekosongan (%)": round(missing.mean() * 100, 2)
        })
    return pd.DataFrame(rows).sort_values("Kelengkapan (%)")

def get_problem_summary(df):
    problem = df[df["Aset_Bermasalah"].eq(1)].copy()
    if problem.empty:
        return pd.DataFrame(columns=["Bagian", "Lokasi", "Jumlah", "Aset_Bermasalah"])
    return problem.groupby(["Bagian", "Lokasi"], dropna=False).agg(
        Jumlah=("Jumlah", "sum"),
        Aset_Bermasalah=("Aset_Bermasalah", "sum")
    ).reset_index()
