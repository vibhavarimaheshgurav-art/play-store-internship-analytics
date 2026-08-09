from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go


DATA_PATH = Path(__file__).parent.parent / "data" / "Play Store Data.csv"


def load_task3_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["Category", "Installs", "Type", "Price", "Android Ver", "Size"]).copy()

    df["Installs"] = (
        df["Installs"].astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.strip()
    )
    df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce")

    df["Price"] = df["Price"].astype(str).str.replace("$", "", regex=False).str.strip()
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    def convert_size(val):
        if pd.isna(val) or str(val).strip() in ("Varies with device", ""):
            return None
        val = str(val).strip()
        try:
            if val.endswith("M"):
                return float(val[:-1])
            if val.endswith("k"):
                return float(val[:-1]) / 1024
            return float(val)
        except (ValueError, TypeError):
            return None

    df["Size"] = df["Size"].apply(convert_size)

    df["Android_Ver_Numeric"] = (
        df["Android Ver"].astype(str).str.extract(r"(\d+\.\d+)", expand=False)
    )
    df["Android_Ver_Numeric"] = pd.to_numeric(df["Android_Ver_Numeric"], errors="coerce")

    df["App_Name_Length"] = df["App"].astype(str).str.len()

    # Revenue = Price * Installs for Paid apps; 0 for Free apps
    df["Revenue"] = 0.0
    paid = df["Type"] == "Paid"
    df.loc[paid, "Revenue"] = df.loc[paid, "Price"] * df.loc[paid, "Installs"]

    df = df.dropna(subset=["Installs", "Price", "Size", "Android_Ver_Numeric", "Revenue"])
    return df


def apply_task3_filters(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["Installs"] >= 10_000]
    df = df[(df["Type"] == "Free") | (df["Revenue"] >= 10_000)]
    df = df[df["Android_Ver_Numeric"] > 4.0]
    df = df[df["Size"] > 15]
    df = df[df["Content Rating"] == "Everyone"]
    df = df[df["App_Name_Length"] <= 30]
    return df


def get_task3_chart_data():
    df = load_task3_data()
    df = apply_task3_filters(df)

    top_categories = (
        df.groupby("Category", as_index=False)["Installs"]
        .sum()
        .sort_values("Installs", ascending=False)
        .head(3)["Category"]
        .tolist()
    )

    df_top = df[df["Category"].isin(top_categories)].copy()

    summary = (
        df_top.groupby(["Category", "Type"], as_index=False)
        .agg({"Installs": "mean", "Revenue": "mean", "App": "count"})
        .rename(columns={"App": "App_Count"})
        .sort_values(["Category", "Type"])
    )
    return summary, top_categories


def build_task3_figure():
    try:
        summary, _ = get_task3_chart_data()
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error loading data: {e}", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    if summary.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available after applying filters.", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    fig = go.Figure()
    colors = {"Free": "#0066cc", "Paid": "#ff6633"}

    for app_type in ["Free", "Paid"]:
        type_data = summary[summary["Type"] == app_type]
        fig.add_trace(go.Scatter(
            x=type_data["Category"],
            y=type_data["Installs"],
            name=f"{app_type} Apps - Avg Installs",
            mode="lines+markers",
            line=dict(color=colors[app_type], width=2),
            marker=dict(size=10),
            hovertemplate="<b>%{x}</b><br>Avg Installs: %{y:,.0f}<extra></extra>",
            yaxis="y1",
        ))
        fig.add_trace(go.Scatter(
            x=type_data["Category"],
            y=type_data["Revenue"],
            name=f"{app_type} Apps - Avg Revenue",
            mode="lines+markers",
            line=dict(color=colors[app_type], width=2, dash="dash"),
            marker=dict(size=10, symbol="diamond"),
            hovertemplate="<b>%{x}</b><br>Avg Revenue: $%{y:,.2f}<extra></extra>",
            yaxis="y2",
        ))

    fig.update_layout(
        title={"text": "Free vs Paid Apps: Average Installs and Revenue (Top 3 Categories)", "x": 0.5, "xanchor": "center"},
        xaxis=dict(title="App Category"),
        yaxis=dict(title="Average Installs", title_font=dict(color="#0066cc"), tickfont=dict(color="#0066cc")),
        yaxis2=dict(title="Average Revenue ($)", title_font=dict(color="#ff6633"), tickfont=dict(color="#ff6633"), overlaying="y", side="right"),
        hovermode="x unified",
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="gray", borderwidth=1),
        template="plotly_white",
        margin={"l": 90, "r": 90, "t": 100, "b": 70},
        height=600,
        autosize=True,
    )
    return fig


def is_task3_allowed_window() -> bool:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return 13 <= now.hour < 14


def get_task3_summary_stats():
    try:
        df = load_task3_data()
        df_filtered = apply_task3_filters(df)
        _, top_categories = get_task3_chart_data()
        return {
            "status": "success",
            "original_rows": len(df),
            "filtered_rows": len(df_filtered),
            "top_3_categories": top_categories,
            "free_apps": len(df_filtered[df_filtered["Type"] == "Free"]),
            "paid_apps": len(df_filtered[df_filtered["Type"] == "Paid"]),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("Task 3: Dual-Axis Chart")
    print(get_task3_summary_stats())
    print(f"Time window active: {is_task3_allowed_window()}")
