

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go


DATA_PATH = Path(__file__).parent.parent / "data" / "Play Store Data.csv"

CATEGORY_LABELS = {
    "BEAUTY": "Beauty (सौंदर्य)",
    "BUSINESS": "Business (வணிகம்)",
    "DATING": "Dating (Partnersuche)",
}


def load_task4_data() -> pd.DataFrame:
    """Load, clean, and filter the Play Store data for Task 4."""
    df = pd.read_csv(DATA_PATH)

    df = df.dropna(subset=["App", "Category", "Reviews", "Installs", "Last Updated"]).copy()
    df = df.drop_duplicates(subset=["App", "Category", "Reviews", "Installs", "Last Updated"], keep="first")

    df["App"] = df["App"].fillna("Unknown").astype(str)
    df["Category"] = df["Category"].fillna("Unknown").astype(str)

    df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce")
    df["Installs"] = (
        df["Installs"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.strip()
    )
    df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce")
    df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")

    df = df.dropna(subset=["Reviews", "Installs", "Last Updated"])

    df = df[df["Reviews"] > 500]
    df = df[df["Category"].astype(str).str.upper().str.startswith(("B", "C", "E", "D"), na=False)]
    df = df[~df["App"].astype(str).str.upper().str.startswith(("X", "Y", "Z"), na=False)]
    df = df[~df["App"].astype(str).str.contains("[Ss]", na=False)]

    df["Category_Display"] = df["Category"].map(CATEGORY_LABELS).fillna(df["Category"])
    df["Month"] = df["Last Updated"].dt.to_period("M").dt.to_timestamp()

    return df


def prepare_task4_chart_data() -> pd.DataFrame:
    """Aggregate installs by month and category for plotting."""
    df = load_task4_data()
    if df.empty:
        return pd.DataFrame(columns=["Month", "Category", "Total Installs"])

    summary = (
        df.groupby(["Month", "Category_Display"], as_index=False)["Installs"]
        .sum()
        .rename(columns={"Category_Display": "Category", "Installs": "Total Installs"})
    )
    if not summary.empty:
        all_months = pd.date_range(start=summary["Month"].min(), end=summary["Month"].max(), freq="MS")
        all_categories = summary["Category"].unique()
        full_idx = pd.MultiIndex.from_product([all_months, all_categories], names=["Month", "Category"])
        summary = (
            summary.set_index(["Month", "Category"])
            .reindex(full_idx, fill_value=0)
            .reset_index()
            .sort_values(["Category", "Month"])
        )
    return summary


def build_task4_figure() -> go.Figure:
    """Create an interactive time series chart for monthly installs by category."""
    try:
        summary = prepare_task4_chart_data()
    except Exception as exc:
        fig = go.Figure()
        fig.add_annotation(text=f"Error processing data: {exc}", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    if summary.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available after applying the requested filters.", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    fig = go.Figure()
    categories = sorted(summary["Category"].unique())
    colors = {
        "Beauty (सौंदर्य)": "#4C78A8",
        "Business (வணிகம்)": "#F58518",
        "Dating (Partnersuche)": "#54A24B",
        "COMMUNICATION": "#E45756",
        "EDUCATION": "#72B7B2",
    }

    for category in categories:
        category_data = summary[summary["Category"] == category].sort_values("Month")
        category_data = category_data.copy()
        category_data["GrowthPct"] = category_data["Total Installs"].pct_change() * 100

        line_color = colors.get(category, "#1f77b4")
        fig.add_trace(
            go.Scatter(
                x=category_data["Month"],
                y=category_data["Total Installs"],
                mode="lines+markers",
                name=category,
                line=dict(color=line_color, width=2.5),
                marker=dict(size=7),
                hovertemplate=(
                    f"<b>{category}</b><br>"
                    "Month: %{x|%b %Y}<br>"
                    "Total Installs: %{y:,.0f}<br>"
                    "Growth: %{customdata:,.1f}%<extra></extra>"
                ),
                customdata=category_data["GrowthPct"],
            )
        )

        highlight_mask = category_data["GrowthPct"] > 20
        if highlight_mask.any():
            highlight_x = category_data.loc[highlight_mask, "Month"]
            highlight_y = category_data.loc[highlight_mask, "Total Installs"]
            fig.add_trace(
                go.Scatter(
                    x=highlight_x,
                    y=highlight_y,
                    mode="lines",
                    line=dict(width=0),
                    fill="tozeroy",
                    fillcolor=_hex_to_rgba(line_color, 0.25),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    fig.update_layout(
        title={
            "text": "Monthly Total Installs by App Category",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "#23395d"},
        },
        xaxis=dict(
            title="Month",
            type="date",
            tickformat="%b %Y",
            showgrid=True,
            gridcolor="#e5e7eb",
        ),
        yaxis=dict(
            title="Total Installs",
            showgrid=True,
            gridcolor="#e5e7eb",
            rangemode="tozero",
        ),
        hovermode="x unified",
        template="plotly_white",
        legend=dict(title="Category", bgcolor="rgba(255,255,255,0.9)"),
        margin=dict(l=70, r=30, t=80, b=60),
        height=650,
        autosize=True,
    )
    return fig


def is_task4_allowed_window() -> bool:
    """Return True only between 6 PM and 9 PM IST."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return 18 <= now.hour < 21


def get_task4_summary_stats() -> dict:
    """Return a small summary of the filtered dataset for display."""
    try:
        df = load_task4_data()
        return {
            "status": "success",
            "rows_after_filter": len(df),
            "categories": sorted(df["Category_Display"].unique().tolist()),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex color to an rgba string."""
    color = hex_color.lstrip("#")
    rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("Task 4: Monthly Install Trend Analysis")
    print("=" * 42)
    print(get_task4_summary_stats())
    print(f"Current time allows visualization: {is_task4_allowed_window()}")
