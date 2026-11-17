import io
import textwrap
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_processing import load_inventory
from utils.analytics import get_kpis, get_data_quality, get_problem_summary
from utils.visualizations import (
    status_donut, condition_pie, horizontal_bar, condition_by_status,
    pareto_chart, completeness_chart
)

BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = BASE_DIR / "assets" / "logo_pdam_full.png"
ICON_PATH = BASE_DIR / "assets" / "logo_pdam_icon.png"
if not LOGO_PATH.exists():
    LOGO_PATH = BASE_DIR / "logo_pdam_full.png"
if not ICON_PATH.exists():
    ICON_PATH = BASE_DIR / "logo_pdam_icon.png"

st.set_page_config(
    page_title="ASSET INSIGHT | PDAM Surya Sembada",
    page_icon=str(ICON_PATH) if ICON_PATH.exists() else "📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY, BLUE, TEAL = "#173B75", "#2457A7", "#168F91"
DATA_PATH = BASE_DIR / "data" / "data_inventaris_analitik.csv"


def pareto_chart(data, dimension, title):
    """Horizontal Pareto chart with readable category labels."""
    if data.empty or dimension not in data.columns:
        fig = go.Figure()
        fig.update_layout(title=title, annotations=[dict(
            text="Tidak ada aset bermasalah pada filter ini",
            x=.5, y=.5, xref="paper", yref="paper", showarrow=False
        )])
        return fig

    agg = (
        data.groupby(dimension, dropna=False)["Jumlah"]
        .sum().sort_values(ascending=False).reset_index()
    )
    agg[dimension] = agg[dimension].fillna("Tidak diketahui").astype(str)
    agg["Kumulatif (%)"] = agg["Jumlah"].cumsum() / agg["Jumlah"].sum() * 100
    agg["Label"] = agg[dimension].map(
        lambda value: textwrap.fill(value, width=28, break_long_words=False)
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["Jumlah"], y=agg["Label"], orientation="h",
        name="Jumlah aset bermasalah", marker_color="#168F91",
        text=agg["Jumlah"].map(lambda value: f"{value:,.0f}"),
        textposition="outside", cliponaxis=False,
        customdata=agg[[dimension, "Kumulatif (%)"]],
        hovertemplate=(
            "%{customdata[0]}<br>Jumlah: %{x:,.0f} unit"
            "<br>Kumulatif: %{customdata[1]:.1f}%<extra></extra>"
        )
    ))
    fig.add_trace(go.Scatter(
        x=agg["Kumulatif (%)"], y=agg["Label"], xaxis="x2",
        mode="lines+markers", name="Persentase kumulatif",
        line=dict(color="#E8755A", width=2.5), marker=dict(size=7),
        hovertemplate="Kumulatif: %{x:.1f}%<extra></extra>"
    ))
    height = max(470, min(1250, 34 * len(agg) + 170))
    fig.update_layout(
        title=dict(text=title, x=.02, xanchor="left"),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color="#26384d", size=12),
        xaxis=dict(
            title="Jumlah unit aset bermasalah",
            showgrid=True, gridcolor="#e7edf4", zeroline=False,
            automargin=True
        ),
        xaxis2=dict(
            title="Persentase kumulatif", overlaying="x", side="top",
            range=[0, 108], ticksuffix="%", showgrid=False, zeroline=False
        ),
        yaxis=dict(
            title="", autorange="reversed",
            categoryorder="array", categoryarray=agg["Label"].tolist(),
            tickfont=dict(size=11), automargin=True, showgrid=False
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.10,
            xanchor="right", x=1, title_text=""
        ),
        margin=dict(l=40, r=75, t=115, b=55),
        bargap=.28
    )
    return fig

st.markdown(f"""
<style>
.stApp {{background:linear-gradient(135deg,#f5f8fc 0%,#edf4fa 58%,#f5fbfa 100%);}}
section[data-testid="stSidebar"] {{
    background:linear-gradient(180deg,{NAVY} 0%,#214b8c 72%,#176f7a 125%);
    width:320px !important; min-width:320px !important; max-width:320px !important;
}}
section[data-testid="stSidebar"] > div {{width:320px !important;}}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
    padding:1.0rem 1.05rem 1.1rem 1.05rem !important;
}}
section[data-testid="stSidebar"] [data-testid="stElementContainer"],
section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    width:100% !important; max-width:100% !important;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {{
    width:100% !important; text-align:center !important;
    margin:.85rem auto .25rem auto !important; font-size:1.35rem !important;
}}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
    width:100% !important; text-align:center !important;
}}
section[data-testid="stSidebar"] .sidebar-brand {{
    width:100%; text-align:center !important; display:block;
    font-size:1.35rem; font-weight:800; letter-spacing:.02em;
}}
section[data-testid="stSidebar"] .sidebar-subtitle {{
    width:100%; text-align:center !important; display:block;
}}
section[data-testid="stSidebar"] [data-testid="stImage"] {{
    width:100% !important; display:flex !important; justify-content:center !important;
    margin:0 auto .7rem auto !important;
}}
section[data-testid="stSidebar"] [data-testid="stImage"] img {{
    width:100% !important; max-width:245px !important; max-height:72px !important;
    object-fit:contain !important; object-position:center !important;
}}
[data-testid="stSidebar"] * {{color:#f7fbff;}}
.block-container {{padding-top:2.35rem; padding-bottom:1.5rem; padding-left:1.6rem; padding-right:1.6rem;}}
.page-intro {{color:#64748b;font-size:.94rem;margin-top:-.2rem;margin-bottom:1rem;}}
.page-counter {{
    min-height:42px; margin-top:1.78rem; padding:.55rem .9rem;
    border-radius:10px; text-align:center; font-weight:800;
    color:#fff; background:linear-gradient(105deg,#2457A7,#168F91);
    box-shadow:0 3px 10px rgba(23,59,117,.12);
}}
.page-counter span {{display:block;font-size:.78rem;font-weight:500;color:#eaf6ff;margin-top:.12rem;}}
.hero {{display:flex;align-items:center;gap:1.2rem;}}
.hero-copy {{flex:1;}}
[data-testid="stSidebar"] .sidebar-nav-title {{
    width:100%; display:block; text-align:center !important;
    font-weight:800; letter-spacing:.08em; margin:1rem 0 1rem 0;
}}
section[data-testid="stSidebar"] [data-testid="stButton"],
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(> div [data-testid="stButton"]) {{
    width:100% !important; max-width:100% !important;
    display:block !important; margin:.42rem 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stButton"] > button {{
    box-sizing:border-box !important; display:flex !important;
    align-items:center !important; justify-content:center !important;
    width:100% !important; min-width:100% !important; max-width:100% !important;
    height:54px !important; min-height:54px !important; max-height:54px !important;
    margin:0 !important; padding:.45rem .6rem !important;
    border:1px solid rgba(255,255,255,.20) !important; border-radius:13px !important;
    background:rgba(255,255,255,.075) !important; color:#f7fbff !important;
    text-align:center !important; white-space:nowrap !important;
}}
section[data-testid="stSidebar"] [data-testid="stButton"] > button > div {{
    width:100% !important; display:flex !important; align-items:center !important;
    justify-content:center !important; flex-direction:row !important;
    gap:.55rem !important; white-space:nowrap !important;
}}
section[data-testid="stSidebar"] [data-testid="stButton"] > button p {{
    width:auto !important; margin:0 !important; padding:0 !important;
    text-align:center !important; white-space:nowrap !important;
    flex:0 0 auto !important;
}}
section[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {{
    background:linear-gradient(105deg,#2457A7,#168F91) !important;
    color:white !important; border-color:rgba(255,255,255,.28) !important;
}}
section[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {{
    background:rgba(54,181,189,.28) !important; border-color:#36B5BD !important;
    color:white !important;
}}
.hero {{background:linear-gradient(110deg,{NAVY} 0%,{BLUE} 52%,{TEAL} 100%);
padding:1.2rem 1.5rem;border-radius:18px;color:white;margin-bottom:1rem;}}
.hero h1 {{color:white;margin:0;font-size:1.8rem;}}
.hero p {{color:#e5f2ff;margin:.35rem 0 0 0;}}
.metric-card {{padding:1rem 1.1rem;border-radius:16px;color:white;
box-shadow:0 5px 16px rgba(23,59,117,.13);min-height:112px;}}
.metric-label {{font-size:.82rem;opacity:.94;font-weight:650;}}
.metric-value {{font-size:1.9rem;font-weight:800;margin:.25rem 0;}}
.metric-note {{font-size:.76rem;opacity:.9;}}
.quality-kpi {{margin-bottom:.85rem; min-height:122px; display:flex; flex-direction:column; justify-content:center;}}
.quality-kpi-blue {{background:linear-gradient(120deg,#173B75 0%,#2457A7 100%);}}
.quality-kpi-teal {{background:linear-gradient(120deg,#168F91 0%,#36B5BD 100%);}}
.quality-note {{color:#64748b;line-height:1.55;padding:.15rem .1rem;}}
.priority-range {{display:block;font-size:1.08rem;font-weight:800;margin:.35rem 0 .45rem 0;color:#203b60;}}
div[data-testid="stDataFrame"] {{border:1px solid #dbe5ef;border-radius:12px;}}
.stApp [data-testid="stButton"] button[kind="primary"] {{
    background:linear-gradient(110deg,#2457A7 0%,#168F91 100%);
    color:#fff; border:1px solid rgba(255,255,255,.18); border-radius:11px;
    min-height:44px; font-weight:650;
}}
.stApp [data-testid="stButton"] button[kind="primary"]:hover {{
    background:linear-gradient(110deg,#1d4b91 0%,#117b7e 100%); color:#fff;
}}
h2,h3 {{color:#203b60;}}
[data-testid="stVerticalBlock"] {{gap:.72rem;}}
.st-key-monitoring_filter_actions [data-testid="stHorizontalBlock"] {{gap:.75rem;}}
.st-key-monitoring_filter_actions [data-testid="stButton"] button {{
    width:100%; min-height:46px; height:46px; border-radius:11px;
    font-weight:650;
}}
.st-key-monitoring_reset,
div[class*="st-key-monitoring_reset"] {{width:100% !important;}}
.st-key-monitoring_reset button,
div[class*="st-key-monitoring_reset"] button {{
    width:100% !important; min-height:46px !important; height:46px !important;
    background:linear-gradient(110deg,#C94F4F 0%,#E36A5C 100%) !important;
    background-color:#C94F4F !important; color:#fff !important;
    border:1px solid #d45d54 !important; border-radius:11px !important;
}}
.st-key-monitoring_reset button:hover,
div[class*="st-key-monitoring_reset"] button:hover {{
    background:linear-gradient(110deg,#ad3d3d 0%,#ca5148 100%) !important;
    background-color:#ad3d3d !important; color:#fff !important;
}}
[data-testid="stHorizontalBlock"] {{gap:.85rem;}}
/* Pagination: both controls use the dashboard palette and stay visibly colored. */
.st-key-monitoring_pagination [data-testid="stButton"] button {{
    width:100% !important; min-height:42px !important; height:42px !important;
    border-radius:10px !important; font-weight:700 !important;
    color:#ffffff !important; border:1px solid rgba(255,255,255,.22) !important;
    background:linear-gradient(110deg,#2457A7 0%,#168F91 100%) !important;
    opacity:1 !important; box-shadow:0 3px 9px rgba(23,59,117,.12) !important;
}}
.st-key-monitoring_pagination [data-testid="stButton"] button:hover:not(:disabled) {{
    background:linear-gradient(110deg,#1d4b91 0%,#117b7e 100%) !important;
    border-color:#36B5BD !important; color:#ffffff !important;
}}
.st-key-monitoring_pagination [data-testid="stButton"] button:disabled {{
    background:linear-gradient(110deg,#7894bd 0%,#78aaa9 100%) !important;
    color:#ffffff !important; opacity:.82 !important; cursor:not-allowed !important;
}}
[data-testid="stExpander"] {{border-radius:11px;}}
[data-testid="stPlotlyChart"] {{margin:.15rem 0 .35rem 0;}}
[data-testid="stPlotlyChart"] {{background:rgba(255,255,255,.8);border:1px solid #e2eaf2;border-radius:14px;padding:.35rem;}}
div[data-testid="stMetric"] {{background:#ffffff;border:1px solid #dfe8f2;border-radius:14px;padding:1rem 1.1rem;box-shadow:0 3px 12px rgba(23,59,117,.06);}}
div[data-testid="stMetric"] label {{color:#52657d;font-weight:650;}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{color:#173B75;font-weight:750;}}

/* Download controls: equal width, centered, and consistent with the dashboard palette */
.download-row {{display:flex;justify-content:center;align-items:center;gap:1rem;margin:.6rem auto 1rem auto;}}
div[data-testid="stDownloadButton"] button {{
    width:100%; min-height:46px; border-radius:11px;
    border:1px solid rgba(255,255,255,.18);
    background:linear-gradient(110deg,#2457A7 0%,#168F91 100%);
    color:#ffffff; font-weight:650;
    box-shadow:0 4px 12px rgba(23,59,117,.12);
}}
div[data-testid="stDownloadButton"] button:hover {{
    color:#ffffff; border-color:#168F91;
    background:linear-gradient(110deg,#1d4b91 0%,#117b7e 100%);
}}
.priority-guide {{background:#ffffff;border:1px solid #dbe5ef;border-radius:14px;
    padding:1.15rem 1.35rem;margin:.7rem 0 1.3rem 0;line-height:1.65;}}
.priority-guide h4 {{margin:.1rem 0 .65rem 0;color:#203b60;}}
.priority-guide p {{margin:.45rem 0;color:#334155;}}
.priority-guide .guide-grid {{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem;margin-top:.85rem;}}
.priority-guide .guide-item {{padding:1rem;border-radius:12px;border:1px solid transparent;line-height:1.6;}}
.priority-guide .guide-item.high {{background:#fff0ed;border-color:#f3c2b8;}}
.priority-guide .guide-item.medium {{background:#fff7e6;border-color:#f0d69b;}}
.priority-guide .guide-item.low {{background:#eaf6f3;border-color:#b8ded5;}}
.priority-guide .guide-item strong {{display:block;margin-bottom:.55rem;color:#203b60;}}
.priority-guide .guide-note {{font-size:.88rem;color:#64748b;margin-top:.8rem;}}
@media (max-width: 760px) {{.priority-guide .guide-grid {{grid-template-columns:1fr;}}}}

</style>
""", unsafe_allow_html=True)

df_raw = load_inventory(DATA_PATH)
if df_raw.empty:
    st.error("Data inventaris belum tersedia. Periksa file data/data_inventaris_analitik.csv.")
    st.stop()

NAV_ITEMS = [
    ("Dashboard", ":material/dashboard:"),
    ("Monitoring", ":material/monitoring:"),
    ("Distribusi Inventaris", ":material/analytics:"),
    ("Analisis Kondisi", ":material/health_and_safety:"),
    ("Analisis Prioritas", ":material/priority_high:"),
]
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    st.markdown('<div class="sidebar-brand">ASSET INSIGHT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Dashboard Analitik Inventaris</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-nav-title">NAVIGASI UTAMA</div>', unsafe_allow_html=True)
    for label, icon in NAV_ITEMS:
        if st.button(label, key=f"nav_{label}", icon=icon,
                     type="primary" if st.session_state.active_page == label else "secondary"):
            st.session_state.active_page = label
            st.rerun()
    st.markdown("---")
    st.caption("PERUMDA Air Minum Surya Sembada")

page = st.session_state.active_page

if page == "Dashboard":
    st.markdown("""
    <div class="hero"><div class="hero-copy">
      <h1>ASSET INSIGHT</h1>
      <p>Dashboard Analitik dan Monitoring Inventaris Aset<br>
      PERUMDA Air Minum Surya Sembada Kota Surabaya</p>
    </div></div>
    """, unsafe_allow_html=True)

filtered = df_raw.copy()

if page == "Dashboard":
    st.subheader("Ringkasan Inventaris")
    kpis = get_kpis(filtered)
    metric_specs = [
        ("TOTAL UNIT ASET", kpis["total"], "Jumlah unit inventaris", "linear-gradient(120deg,#173B75,#2457A7)"),
        ("ASET AKTIF", kpis["active"], "Status aktif", "linear-gradient(120deg,#168F91,#36B5BD)"),
        ("ASET TIDAK AKTIF", kpis["inactive"], "Status tidak aktif", "linear-gradient(120deg,#2457A7,#36B5BD)"),
        ("ASET BERMASALAH", kpis["attention"], f"Problem rate {kpis['problem_rate']:.2f}%", "linear-gradient(120deg,#B7791F,#E8755A)"),
    ]
    cols = st.columns(4)
    for col, (label, value, note, gradient) in zip(cols, metric_specs):
        col.markdown(f"""<div class="metric-card" style="background:{gradient}">
        <div class="metric-label">{label}</div><div class="metric-value">{value:,.0f}</div>
        <div class="metric-note">{note}</div></div>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(condition_pie(filtered), use_container_width=True)
    with c2:
        st.plotly_chart(status_donut(filtered), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(horizontal_bar(filtered, "Kategori", "Jumlah", "10 Kategori dengan Unit Aset Terbanyak"), use_container_width=True)
    with c4:
        st.plotly_chart(horizontal_bar(filtered, "Bagian", "Jumlah", "10 Bagian dengan Unit Aset Terbanyak"), use_container_width=True)

    # Kualitas data tetap tersedia sebagai informasi pendukung, bukan menu utama.
    with st.expander("Pemeriksaan Kualitas dan Kelengkapan Data"):
        quality = get_data_quality(filtered)
        q1, q2 = st.columns([1.4, 1])
        with q1:
            st.plotly_chart(completeness_chart(quality), use_container_width=True)
        with q2:
            avg_quality = quality["Kelengkapan (%)"].mean()
            checked_attributes = len(quality)
            st.markdown(f"""
            <div class="metric-card quality-kpi quality-kpi-blue">
              <div class="metric-label">Rata-rata kelengkapan atribut</div>
              <div class="metric-value">{avg_quality:.1f}%</div>
            </div>
            <div class="metric-card quality-kpi quality-kpi-teal">
              <div class="metric-label">Atribut yang diperiksa</div>
              <div class="metric-value">{checked_attributes}</div>
            </div>
            <div class="quality-note">
              Membantu menemukan atribut inventaris yang masih perlu dilengkapi.
            </div>
            """, unsafe_allow_html=True)
        st.dataframe(quality, use_container_width=True, hide_index=True)

elif page == "Distribusi Inventaris":
    st.subheader("Distribusi Inventaris")
    st.markdown('<div class="page-intro">Pilih kelompok inventaris yang ingin dilihat dan atur banyaknya kategori pada grafik.</div>', unsafe_allow_html=True)

    filter_col, limit_col = st.columns([2, 1])
    with filter_col:
        distribution_dimension = st.selectbox(
            "Tampilkan distribusi berdasarkan",
            ["Bagian", "Lokasi", "Kategori"],
            key="distribution_dimension"
        )
    with limit_col:
        distribution_limit = st.select_slider(
            "Jumlah kategori pada grafik",
            options=[5, 8, 10, 12, 15, 20, 25, 30],
            value=12,
            key="distribution_limit"
        )

    st.plotly_chart(
        horizontal_bar(
            filtered, distribution_dimension, "Jumlah",
            f"Distribusi Unit Aset menurut {distribution_dimension}",
            limit=int(distribution_limit)
        ),
        use_container_width=True
    )

    st.markdown("#### Rincian Distribusi")
    distribution_summary = (
        filtered.groupby(distribution_dimension, dropna=False)["Jumlah"]
        .sum().reset_index()
        .sort_values("Jumlah", ascending=False)
        .rename(columns={"Jumlah": "Jumlah Unit"})
    )
    st.dataframe(
        distribution_summary.head(int(distribution_limit)),
        use_container_width=True, hide_index=True
    )

elif page == "Analisis Kondisi":
    st.subheader("Analisis Kondisi Aset")
    st.markdown('<div class="page-intro">Membandingkan kondisi fisik aset dan status penggunaannya sebagai dasar pemantauan serta tindak lanjut pemeliharaan.</div>', unsafe_allow_html=True)
    st.caption("Ringkasan komposisi kondisi dan perbandingan kondisi berdasarkan status penggunaan.")
    st.plotly_chart(condition_pie(filtered), use_container_width=True)
    st.plotly_chart(condition_by_status(filtered), use_container_width=True)
    pivot = pd.pivot_table(filtered, index="Kondisi", columns="Status", values="Jumlah",
                           aggfunc="sum", fill_value=0).reset_index()
    st.markdown("#### Rincian Kondisi menurut Status")
    st.dataframe(pivot, use_container_width=True, hide_index=True)

elif page == "Analisis Prioritas":
    st.subheader("Analisis Prioritas Evaluasi Aset")
    st.caption("Lokasi diurutkan berdasarkan proporsi aset bermasalah untuk membantu menentukan fokus pemeriksaan.")

    problem = get_problem_summary(filtered)
    location_data = filtered.copy()
    location_data["Aset_Bermasalah"] = (
        location_data["Kondisi"].astype(str).str.strip().str.lower()
        .isin(["kurang baik", "dalam perbaikan", "rusak"])
    )
    location_summary = location_data.groupby("Lokasi", dropna=False).apply(
        lambda g: pd.Series({
            "Total Aset": g["Jumlah"].sum(),
            "Aset Bermasalah": g.loc[g["Aset_Bermasalah"], "Jumlah"].sum()
        })
    ).reset_index()
    location_summary["Problem Rate (%)"] = (
        location_summary["Aset Bermasalah"]
        .div(location_summary["Total Aset"].replace(0, pd.NA))
        .mul(100).fillna(0).round(2)
    )
    location_summary = location_summary.sort_values(
        ["Problem Rate (%)", "Aset Bermasalah"], ascending=False
    ).reset_index(drop=True)

    # Kategori relatif: membagi lokasi ke tiga kelompok berdasarkan peringkat Problem Rate.
    if len(location_summary):
        relative_rank = location_summary["Problem Rate (%)"].rank(method="average", pct=True)
        location_summary["Kategori Prioritas"] = pd.cut(
            relative_rank,
            bins=[0, 1/3, 2/3, 1.000001],
            labels=["Rendah", "Menengah", "Tinggi"],
            include_lowest=True
        ).astype(str)
    else:
        location_summary["Kategori Prioritas"] = []

    # Rentang persentase aktual tiap kategori dihitung dari lokasi yang sedang dianalisis.
    priority_ranges = {}
    for category in ["Tinggi", "Menengah", "Rendah"]:
        values = location_summary.loc[
            location_summary["Kategori Prioritas"] == category, "Problem Rate (%)"
        ]
        priority_ranges[category] = (
            f"{values.min():.2f}%–{values.max():.2f}%" if not values.empty else "Tidak ada lokasi"
        )

    total_units = location_summary["Total Aset"].sum()
    problem_units = location_summary["Aset Bermasalah"].sum()
    overall_rate = problem_units / total_units * 100 if total_units else 0

    metric_specs = [
        ("TOTAL UNIT ASET", total_units, "Seluruh unit inventaris", "linear-gradient(120deg,#173B75,#2457A7)"),
        ("ASET BERMASALAH", problem_units, "Kurang Baik, Dalam Perbaikan, dan Rusak", "linear-gradient(120deg,#B7791F,#E8755A)"),
        ("PROBLEM RATE", overall_rate, "Proporsi unit aset bermasalah", "linear-gradient(120deg,#168F91,#36B5BD)")
    ]
    metric_cols = st.columns(3)
    for col, (label, value, note, gradient) in zip(metric_cols, metric_specs):
        shown_value = f"{value:,.2f}%" if label == "PROBLEM RATE" else f"{value:,.0f}"
        col.markdown(
            f"""<div class="metric-card" style="background:{gradient};min-height:112px;">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{shown_value}</div>
            <div class="metric-note">{note}</div></div>""",
            unsafe_allow_html=True
        )

    with st.expander("Cara membaca Problem Rate dan kategori prioritas", expanded=False):
        st.markdown(
            f"""
            <div class="priority-guide">
              <h4>Apa arti Problem Rate?</h4>
              <p>Problem Rate menunjukkan persentase unit aset bermasalah dibandingkan seluruh unit aset pada lokasi yang sama. Secara matematis, nilainya dapat berada pada rentang <strong>0% sampai 100%</strong>.</p>
              <p><strong>Rumus:</strong> Aset Bermasalah ÷ Total Aset × 100%</p>
              <p>Aset bermasalah adalah unit dengan kondisi <strong>Kurang Baik</strong>, <strong>Dalam Perbaikan</strong>, atau <strong>Rusak</strong>.</p>
              <p><strong>Contoh:</strong> Problem Rate 27,05% berarti sekitar 27 dari setiap 100 unit aset di lokasi tersebut tercatat bermasalah. Angka <strong>27,05%</strong> yang muncul sebagai nilai tertinggi pada tampilan ini adalah nilai tertinggi yang ditemukan dalam data lokasi yang sedang dianalisis, <strong>bukan batas maksimum rumus</strong>. Jika seluruh unit aset bermasalah, nilainya mencapai 100%.</p>
              <h4 style="margin-top:1rem;">Arti kategori prioritas</h4>
              <div class="guide-grid">
                <div class="guide-item high"><strong>Prioritas Tinggi</strong>
                  <span class="priority-range">{priority_ranges["Tinggi"]}</span>
                  Fokus pemeriksaan lebih dahulu karena berada pada kelompok Problem Rate tertinggi.</div>
                <div class="guide-item medium"><strong>Prioritas Menengah</strong>
                  <span class="priority-range">{priority_ranges["Menengah"]}</span>
                  Perlu dipantau dan ditindaklanjuti dengan mempertimbangkan jumlah unit bermasalah.</div>
                <div class="guide-item low"><strong>Prioritas Rendah</strong>
                  <span class="priority-range">{priority_ranges["Rendah"]}</span>
                  Tetap lakukan pemeliharaan rutin dan pemantauan kondisi aset.</div>
              </div>
              <p class="guide-note"><strong>Bagaimana kategori ditentukan?</strong> Lokasi diurutkan berdasarkan Problem Rate, lalu dibagi menjadi tiga kelompok berdasarkan peringkat relatif (sepertiga terbawah, tengah, dan teratas). Angka rentang pada setiap kotak menunjukkan nilai terendah hingga tertinggi yang benar-benar ditemukan dalam kelompok tersebut. Karena hanya menampilkan nilai aktual, rentang antar-kelompok bisa memiliki jeda; jeda itu bukan kategori yang hilang atau batas risiko. Kategori ini merupakan alat bantu perbandingan dalam data, bukan ambang risiko resmi PDAM. Rentang dapat berubah ketika filter atau data berubah. Untuk menentukan tindak lanjut, perhatikan juga jumlah unit aset bermasalah, bukan persentasenya saja.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("#### Lokasi yang Perlu Ditinjau")
    st.caption("Urutan dimulai dari Problem Rate tertinggi. Jumlah aset bermasalah tetap perlu diperhatikan, bukan hanya persentasenya.")
    st.dataframe(
        location_summary[
            ["Lokasi", "Total Aset", "Aset Bermasalah", "Problem Rate (%)", "Kategori Prioritas"]
        ],
        use_container_width=True, hide_index=True
    )

    st.markdown("#### Rekomendasi Tindak Lanjut")
    st.markdown(
        "- **Prioritas tinggi:** jadwalkan pemeriksaan lokasi dan verifikasi kondisi aset terlebih dahulu.\n"
        "- **Aset rusak atau dalam perbaikan:** koordinasikan pemeriksaan teknis, status perbaikan, dan kebutuhan tindak lanjut.\n"
        "- **Aset kurang baik:** evaluasi kelayakan dan rencanakan pemeliharaan preventif.\n"
        "- **Semua kategori:** perbarui kondisi aset setelah pemeriksaan agar monitoring tetap akurat."
    )

    st.markdown("#### Sebaran Aset Bermasalah")
    st.plotly_chart(pareto_chart(problem, "Bagian", "Aset Bermasalah menurut Bagian"), use_container_width=True)
    st.plotly_chart(pareto_chart(problem, "Lokasi", "Aset Bermasalah menurut Lokasi"), use_container_width=True)

elif page == "Monitoring":
    st.subheader("Monitoring")
    table_view = df_raw.drop(columns=["Aset_Bermasalah"], errors="ignore").copy()
    filter_columns = [
        "Bagian", "Lokasi", "Kategori", "Nama Barang", "Fungsi / Tipe",
        "Merk", "Ukuran / Spesifikasi", "Warna", "Bahan",
        "Tahun Pembelian", "Kondisi", "Status", "Penanggung Jawab (PIC)"
    ]
    filter_columns = [c for c in filter_columns if c in table_view.columns]

    if "monitoring_applied_filters" not in st.session_state:
        st.session_state.monitoring_applied_filters = {c: "Semua" for c in filter_columns}
    if "monitoring_page" not in st.session_state:
        st.session_state.monitoring_page = 1

    def reset_monitoring_filters():
        st.session_state.monitoring_applied_filters = {c: "Semua" for c in filter_columns}
        for column in filter_columns:
            st.session_state[f"monitoring_option_{column}"] = "Semua"
        st.session_state.monitoring_page = 1
        st.session_state["monitoring_page_select"] = 1

    with st.expander("Filter Data", expanded=True):
        for row_start in range(0, len(filter_columns), 4):
            cols = st.columns(4)
            for col, column in zip(cols, filter_columns[row_start:row_start + 4]):
                with col:
                    options = ["Semua"] + sorted(
                        table_view[column].dropna().astype(str).unique().tolist()
                    )
                    widget_key = f"monitoring_option_{column}"
                    if widget_key not in st.session_state:
                        st.session_state[widget_key] = st.session_state.monitoring_applied_filters.get(column, "Semua")
                    if st.session_state[widget_key] not in options:
                        st.session_state[widget_key] = "Semua"
                    st.selectbox(column, options, key=widget_key)

        with st.container(key="monitoring_filter_actions"):
            c_apply, c_reset = st.columns(2)
            with c_apply:
                apply_clicked = st.button(
                    "Terapkan", type="primary", use_container_width=True,
                    key="monitoring_apply"
                )
            with c_reset:
                st.button(
                    "Reset", type="secondary", use_container_width=True,
                    key="monitoring_reset", on_click=reset_monitoring_filters
                )

    if apply_clicked:
        st.session_state.monitoring_applied_filters = {
            c: st.session_state.get(f"monitoring_option_{c}", "Semua")
            for c in filter_columns
        }
        st.session_state.monitoring_page = 1
        st.session_state["monitoring_page_select"] = 1

    filtered_table = table_view.copy()
    for column, value in st.session_state.monitoring_applied_filters.items():
        if value != "Semua":
            filtered_table = filtered_table[filtered_table[column].astype(str) == str(value)]

    applied_filter_count = sum(
        1 for value in st.session_state.monitoring_applied_filters.values()
        if value != "Semua"
    )
    st.caption(
        f"{applied_filter_count} filter berhasil diterapkan · "
        f"{len(filtered_table):,} dari {len(table_view):,} baris data."
    )

    page_size = 100
    total_rows = len(filtered_table)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    current_page = min(max(1, int(st.session_state.monitoring_page)), total_pages)

    page_options = list(range(1, total_pages + 1))
    # Sinkronkan state sebelum widget dibuat. Jangan sekaligus memberi index/default
    # pada widget yang nilainya sudah dikelola melalui Session State.
    if (
        "monitoring_page_select" not in st.session_state
        or st.session_state["monitoring_page_select"] not in page_options
    ):
        st.session_state["monitoring_page_select"] = current_page

    page_control, page_status = st.columns([1, 2])
    with page_control:
        selected_page = st.selectbox(
            "Halaman data",
            options=page_options,
            format_func=lambda p: f"Halaman {p}",
            key="monitoring_page_select"
        )
    if selected_page != current_page:
        st.session_state.monitoring_page = selected_page
        current_page = selected_page

    start_row = (current_page - 1) * page_size
    end_row = min(start_row + page_size, total_rows)
    with page_status:
        st.markdown(
            f'<div class="page-counter">HALAMAN {current_page:,} / {total_pages:,}'
            f'<span>Menampilkan {start_row + 1 if total_rows else 0:,}–{end_row:,} '
            f'dari {total_rows:,} data</span></div>',
            unsafe_allow_html=True
        )

    display_table = filtered_table.iloc[start_row:end_row].rename(columns={
        "No.": "No", "Kode Asset": "Kode Aset"
    })
    st.dataframe(display_table, use_container_width=True, hide_index=True, height=620)

    with st.container(key="monitoring_pagination"):
        prev_col, next_col = st.columns(2)
        with prev_col:
            st.button(
                "← Sebelumnya", key="monitoring_prev",
                disabled=current_page <= 1, use_container_width=True,
                on_click=lambda: st.session_state.update(
                    monitoring_page=max(1, st.session_state.monitoring_page - 1),
                    monitoring_page_select=max(1, st.session_state.monitoring_page - 1)
                )
            )
        with next_col:
            st.button(
                "Berikutnya →", key="monitoring_next",
                disabled=current_page >= total_pages, use_container_width=True,
                on_click=lambda: st.session_state.update(
                    monitoring_page=min(total_pages, st.session_state.monitoring_page + 1),
                    monitoring_page_select=min(total_pages, st.session_state.monitoring_page + 1)
                )
            )

    export_table = filtered_table.rename(columns={"No.": "No", "Kode Asset": "Kode Aset"})
    csv = export_table.to_csv(index=False).encode("utf-8-sig")
    xlsx_buffer = io.BytesIO()
    with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
        export_table.to_excel(writer, index=False, sheet_name="Monitoring")
    excel_bytes = xlsx_buffer.getvalue()

    @st.dialog("Pratinjau file sebelum diunduh", width="large")
    def preview_export(data, csv_bytes, excel_file_bytes):
        st.markdown("**MONITORING INVENTARIS ASET**")
        st.caption("PERUMDA Air Minum Surya Sembada Kota Surabaya")
        st.caption(f"Pratinjau isi file · {len(data):,} baris · {len(data.columns):,} kolom")
        st.markdown("---")
        st.dataframe(data.head(100), use_container_width=True, hide_index=True, height=430)
        st.caption("Pratinjau menampilkan maksimal 100 baris pertama. Seluruh data hasil filter disertakan dalam file unduhan.")
        st.markdown("---")
        csv_button, excel_button = st.columns(2)
        with csv_button:
            st.download_button(
                "Unduh CSV", csv_bytes, "monitoring_inventaris.csv",
                "text/csv", use_container_width=True, type="primary",
                key="preview_download_csv"
            )
        with excel_button:
            st.download_button(
                "Unduh Excel", excel_file_bytes, "monitoring_inventaris.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary",
                key="preview_download_excel"
            )

    st.markdown("#### Ekspor Data")
    st.caption("Buka pratinjau untuk memeriksa isi file, lalu unduh dalam format CSV atau Excel.")
    preview_col, csv_col, excel_col = st.columns([1.35, 1, 1])
    with preview_col:
        if st.button("Pratinjau Unduhan", use_container_width=True, type="primary"):
            preview_export(export_table, csv, excel_bytes)
    with csv_col:
        st.download_button("Unduh CSV", csv, "monitoring_inventaris.csv", "text/csv", use_container_width=True, type="primary")
    with excel_col:
        st.download_button(
            "Unduh Excel", excel_bytes, "monitoring_inventaris.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary"
        )
