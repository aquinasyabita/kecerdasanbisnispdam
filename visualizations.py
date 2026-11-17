import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLORS = {
    "navy": "#173B75", "blue": "#2457A7", "teal": "#168F91",
    "aqua": "#36B5BD", "amber": "#E9B95B", "coral": "#E8755A",
    "sage": "#83A97E", "slate": "#58758F"
}
CONDITION_COLORS = {
    "Bagus": COLORS["teal"], "Kurang Baik": COLORS["amber"],
    "Dalam Perbaikan": COLORS["slate"], "Sudah Diperbaiki": COLORS["sage"],
    "Rusak": COLORS["coral"]
}
STATUS_COLORS = {"Aktif": COLORS["teal"], "Tidak Aktif": COLORS["coral"]}

def _layout(fig, height=390):
    current_margin = fig.layout.margin.to_plotly_json() if fig.layout.margin else {}
    fig.update_layout(
        height=height,
        margin={k: current_margin.get(k, v) for k, v in {"l": 28, "r": 32, "t": 72, "b": 62}.items()},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color="#26384d", size=12),
        legend=dict(
            orientation="h", yanchor="top", y=-0.18,
            xanchor="center", x=0.5, title_text=""
        ),
        hoverlabel=dict(bgcolor="white")
    )
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#e7edf4", zeroline=False, automargin=True)
    return fig

def _sum(df, col):
    return (df.groupby(col, dropna=False)["Jumlah"].sum()
            .reset_index().sort_values("Jumlah", ascending=False))

def condition_pie(df):
    data = _sum(df, "Kondisi")
    fig = px.pie(
        data, names="Kondisi", values="Jumlah", hole=.36,
        color="Kondisi", color_discrete_map=CONDITION_COLORS,
        title="Proporsi Kondisi Aset"
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{percent:.1%}",
        insidetextfont=dict(color="white", size=13),
        marker=dict(line=dict(color="white", width=2)),
        hovertemplate="%{label}<br>%{value:,.0f} unit<br>%{percent:.1%}<extra></extra>"
    )
    fig.update_layout(margin=dict(l=24, r=24, t=72, b=100), height=450)
    return _layout(fig, 450)

def status_donut(df):
    data = _sum(df, "Status")
    fig = px.pie(
        data, names="Status", values="Jumlah", hole=.55,
        color="Status", color_discrete_map=STATUS_COLORS,
        title="Komposisi Status Penggunaan"
    )
    fig.update_traces(
        textposition="inside", texttemplate="%{percent:.1%}",
        insidetextfont=dict(color="white", size=13),
        marker=dict(line=dict(color="white", width=2)),
        hovertemplate="%{label}<br>%{value:,.0f} unit<br>%{percent:.1%}<extra></extra>"
    )
    return _layout(fig, 450)

def horizontal_bar(df, dimension, metric, title, limit=12):
    data = _sum(df, dimension).head(limit).sort_values(metric)
    fig = px.bar(
        data, x=metric, y=dimension, orientation="h", title=title,
        text=metric, color=metric,
        color_continuous_scale=["#b9dce3", COLORS["teal"]]
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}", textposition="outside",
        cliponaxis=False, marker_line_width=0
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=28, r=48, t=72, b=30))
    return _layout(fig, max(360, 29*len(data)+125))

def condition_by_status(df):
    data = (df.groupby(["Kondisi", "Status"], dropna=False)["Jumlah"]
            .sum().reset_index())
    fig = px.bar(
        data, x="Jumlah", y="Kondisi", color="Status",
        barmode="group", orientation="h",
        color_discrete_map=STATUS_COLORS,
        title="Perbandingan Kondisi Aset menurut Status",
        text="Jumlah"
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}", textposition="outside",
        cliponaxis=False
    )
    fig.update_layout(
        bargap=.28, margin=dict(l=30, r=60, t=72, b=90),
        xaxis_title="Jumlah unit aset", yaxis_title=""
    )
    return _layout(fig, 480)

def pareto_chart(data, dimension, title):
    if data.empty or dimension not in data.columns:
        fig = go.Figure()
        fig.update_layout(title=title, annotations=[dict(
            text="Tidak ada aset bermasalah pada filter ini",
            x=.5, y=.5, xref="paper", yref="paper", showarrow=False
        )])
        return _layout(fig, 390)
    agg = (data.groupby(dimension)["Jumlah"].sum()
           .sort_values(ascending=False).reset_index())
    agg["Kumulatif (%)"] = agg["Jumlah"].cumsum() / agg["Jumlah"].sum() * 100
    fig = go.Figure()
    fig.add_bar(x=agg[dimension], y=agg["Jumlah"], name="Jumlah unit",
                marker_color=COLORS["teal"])
    fig.add_scatter(x=agg[dimension], y=agg["Kumulatif (%)"],
                    name="Kumulatif (%)", yaxis="y2", mode="lines+markers",
                    line=dict(color=COLORS["coral"], width=3))
    fig.update_layout(
        title=title, yaxis=dict(title="Jumlah unit"),
        yaxis2=dict(title="Kumulatif (%)", overlaying="y", side="right",
                    range=[0, 105]),
        margin=dict(l=30, r=55, t=72, b=110)
    )
    return _layout(fig, 450)

def completeness_chart(data):
    fig = px.bar(
        data.sort_values("Kelengkapan (%)"), x="Kelengkapan (%)",
        y="Variabel", orientation="h", title="Kelengkapan Setiap Atribut",
        color="Kelengkapan (%)",
        color_continuous_scale=["#E8755A", "#E9B95B", "#168F91"]
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%", textposition="outside",
        cliponaxis=False
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=35, r=55, t=72, b=25))
    return _layout(fig, max(420, 28*len(data)+100))
