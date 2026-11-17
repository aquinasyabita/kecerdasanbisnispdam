# ASSET INSIGHT — Dashboard Analitik Inventaris PDAM

Prototype dashboard Business Intelligence untuk analisis inventaris aset PERUMDA Air Minum Surya Sembada Kota Surabaya.

## Identitas visual
- Logo PDAM yang diberikan.
- Palet Ocean Gradient: Deep Navy, Ocean Blue, Teal, Aqua, Amber, Coral.
- KPI cards dengan gradasi.

## Fitur
- Dashboard overview dan KPI inventaris
- Distribusi aset per bagian, lokasi, dan kategori
- Analisis kondisi dan status
- Analisis prioritas berdasarkan flag `Aset_Bermasalah` dari notebook
- Pareto lokasi/bagian
- Kualitas dan kelengkapan atribut data
- Detail inventaris, pencarian, filter, ekspor CSV dan Excel

## Sumber data
Aplikasi membaca `data/data_inventaris_analitik.csv`. Kolom `Aset_Bermasalah` mengikuti definisi notebook: kondisi `Kurang Baik`, `Dalam Perbaikan`, dan `Rusak`.

Folder `references/` menyimpan notebook dan workbook hasil analisis sebagai dokumentasi acuan. Periksa kesesuaian data jika sumber diperbarui.

## Menjalankan
1. Ekstrak ZIP.
2. Buka terminal pada folder proyek.
3. Jalankan `pip install -r requirements.txt`.
4. Jalankan `streamlit run app.py` atau klik `JALANKAN_DASHBOARD.bat`.

## Privasi dan deployment
Data inventaris adalah data internal. Jangan unggah repository atau aplikasi ke hosting publik sebelum memperoleh izin PDAM. Gunakan data anonim atau hosting dengan akses terbatas sesuai kebijakan PDAM. Dashboard memakai snapshot file, bukan data real-time.
