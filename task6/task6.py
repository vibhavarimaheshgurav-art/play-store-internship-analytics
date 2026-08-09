"""Task 6: Interactive stacked area chart for cumulative installs by category."""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import re

import pandas as pd
import plotly.graph_objects as go


DATA_PATH = Path(__file__).parent.parent / "data" / "Play Store Data.csv"

CATEGORY_TRANSLATIONS = {
    "TRAVEL_AND_LOCAL": "Voyages et Local",
    "PRODUCTIVITY": "Productividad",
    "PHOTOGRAPHY": "写真",
    "PERSONALIZATION": "Personnalisation",
    "TOOLS": "Herramientas",
    "PARENTING": "育児",
}


def load_data() -> pd.DataFrame:
    """Load the Play Store data."""
    return pd.read_csv(DATA_PATH)


def _convert_size_to_mb(size_value) -> float:
    if pd.isna(size_value):
        return None
    value = str(size_value).strip()
    if value in {"", "Varies with device", "nan", "NaN"}:
        return None
    try:
        if value.endswith("M"):
            return float(value[:-1])
        if value.endswith("k"):
            return float(value[:-1]) / 1024
        return float(value)
    except Exception:
        return None


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Play Store data for Task 6."""
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates()

    required_columns = {"App", "Category", "Rating", "Reviews", "Size", "Installs", "Last Updated"}
    missing = required_columns - set(cleaned.columns)
    if missing:
        raise ValueError(f"Play Store dataset missing columns: {missing}")

    cleaned["App"] = cleaned["App"].fillna("Unknown").astype(str)
    cleaned["Category"] = cleaned["Category"].fillna("Unknown").astype(str)

    cleaned["Installs"] = (
        cleaned["Installs"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.strip()
    )
    cleaned["Installs"] = pd.to_numeric(cleaned["Installs"], errors="coerce")

    cleaned["Rating"] = pd.to_numeric(cleaned["Rating"], errors="coerce")
    cleaned["Reviews"] = pd.to_numeric(cleaned["Reviews"], errors="coerce")
    cleaned["Size_MB"] = cleaned["Size"].apply(_convert_size_to_mb)
    cleaned["Last Updated"] = pd.to_datetime(cleaned["Last Updated"], errors="coerce")

    cleaned = cleaned.dropna(subset=["App", "Category", "Rating", "Reviews", "Installs", "Size_MB", "Last Updated"])
    cleaned = cleaned.reset_index(drop=True)
    return cleaned


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply filters requested for Task 6."""
    filtered = df.copy()
    filtered = filtered[filtered["Rating"] >= 4.2]
    filtered = filtered[filtered["Reviews"] > 1000]
    filtered = filtered[(filtered["Size_MB"] >= 20) & (filtered["Size_MB"] <= 80)]
    filtered = filtered[filtered["Category"].astype(str).str.startswith(("T", "P"), na=False)]
    filtered = filtered[~filtered["App"].astype(str).str.contains(r"\d", regex=True, na=False)]
    return filtered.reset_index(drop=True)


def translate_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Create display names for the legend without changing the source data."""
    translated = df.copy()
    translated["Category_Display"] = translated["Category"].astype(str).str.upper().map(CATEGORY_TRANSLATIONS)
    translated["Category_Display"] = translated["Category_Display"].fillna(translated["Category"])
    return translated


def calculate_cumulative_installs(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate installs by month and category and calculate cumulative installs."""
    summary = df.copy()
    if summary.empty:
        return pd.DataFrame(columns=["Month", "Category", "Total Installs", "Cumulative Installs"])

    summary["Month"] = summary["Last Updated"].dt.to_period("M").dt.to_timestamp()
    summary = summary.groupby(["Month", "Category"], as_index=False)["Installs"].sum()

    # Reindex across complete timeline to ensure smooth stacked area alignment
    all_months = pd.date_range(start=summary["Month"].min(), end=summary["Month"].max(), freq="MS")
    all_categories = summary["Category"].unique()
    full_idx = pd.MultiIndex.from_product([all_months, all_categories], names=["Month", "Category"])

    summary = (
        summary.set_index(["Month", "Category"])
        .reindex(full_idx, fill_value=0)
        .reset_index()
    )
    summary = summary.rename(columns={"Installs": "Total Installs"})
    summary = summary.sort_values(["Category", "Month"]).reset_index(drop=True)

    summary["Cumulative Installs"] = summary.groupby("Category")["Total Installs"].cumsum()
    return summary


def calculate_growth(summary: pd.DataFrame) -> pd.DataFrame:
    """Calculate month-over-month growth percentage and growth intensity flags."""
    growth_df = summary.copy()
    if growth_df.empty:
        return growth_df
    growth_df = growth_df.sort_values(["Category", "Month"]).reset_index(drop=True)
    growth_df["Prev_Month_Installs"] = growth_df.groupby("Category")["Cumulative Installs"].shift(1)
    growth_df["GrowthPct"] = ((growth_df["Cumulative Installs"] - growth_df["Prev_Month_Installs"]) / growth_df["Prev_Month_Installs"].replace(0, pd.NA)) * 100
    growth_df["GrowthPct"] = growth_df["GrowthPct"].fillna(0)
    growth_df["HighGrowth"] = growth_df["GrowthPct"] > 25
    return growth_df


def create_stacked_area_chart(df: pd.DataFrame) -> go.Figure:
    """Create an interactive stacked area chart for cumulative installs."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available after applying the requested filters.", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    summary = calculate_cumulative_installs(df)
    summary = calculate_growth(summary)
    if summary.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available after applying the requested filters.", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    categories = sorted(summary["Category"].astype(str).unique().tolist())
    colors = {
        "TRAVEL_AND_LOCAL": "#4C78A8",
        "PRODUCTIVITY": "#F58518",
        "PHOTOGRAPHY": "#54A24B",
        "PERSONALIZATION": "#E15759",
        "TOOLS": "#B07AA1",
        "PARENTING": "#D37295",
    }

    fig = go.Figure()
    for category in categories:
        category_data = summary[summary["Category"].astype(str) == category].sort_values("Month")
        if category_data.empty:
            continue

        display_label = CATEGORY_TRANSLATIONS.get(category.upper(), category)
        base_color = colors.get(category.upper(), "#1f77b4")
        line_color = base_color
        growth_alpha = 0.75 if category_data["HighGrowth"].any() else 0.45
        marker_sizes = [8 if flag else 4 for flag in category_data["HighGrowth"].tolist()]

        fig.add_trace(
            go.Scatter(
                x=category_data["Month"],
                y=category_data["Cumulative Installs"],
                mode="lines+markers",
                stackgroup="one",
                name=display_label,
                line=dict(color=line_color, width=2.5),
                marker=dict(size=marker_sizes, color=line_color),
                fillcolor=_hex_to_rgba(base_color, growth_alpha),
                hovertemplate=(
                    f"<b>{display_label}</b><br>"
                    "Month: %{x|%b %Y}<br>"
                    "Cumulative Installs: %{y:,.0f}<br>"
                    "Growth: %{customdata:.1f}%<extra></extra>"
                ),
                customdata=category_data["GrowthPct"].tolist(),
            )
        )

    # Add visual highlight bands for any month where growth > 25% for any category
    high_growth_months = summary[summary["HighGrowth"]]["Month"].unique()
    for m in high_growth_months:
        m_start = pd.to_datetime(m)
        m_end = m_start + pd.DateOffset(months=1)
        fig.add_vrect(
            x0=m_start,
            x1=m_end,
            fillcolor="rgba(255, 235, 59, 0.2)",
            layer="below",
            line_width=1,
            line_color="rgba(255, 193, 7, 0.5)",
            annotation_text=">25% Growth",
            annotation_position="top left",
        )

    fig.update_layout(
        title={
            "text": "Cumulative Installs by Category Over Time",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "#23395d"},
        },
        xaxis=dict(title="Month", type="date", tickformat="%b %Y", showgrid=True, gridcolor="#e5e7eb"),
        yaxis=dict(title="Cumulative Installs", showgrid=True, gridcolor="#e5e7eb", rangemode="tozero"),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(title="Category", bgcolor="rgba(255,255,255,0.9)"),
        margin=dict(l=70, r=30, t=80, b=60),
        height=650,
        autosize=True,
    )
    return fig


def is_allowed_time() -> bool:
    """Allow the chart only between 4 PM and 6 PM IST."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return 16 <= now.hour < 18


def build_task6_figure() -> go.Figure:
    """Build the Task 6 figure with graceful error handling."""
    try:
        play_df = load_data()
        cleaned = clean_data(play_df)
        filtered = apply_filters(cleaned)
        translated = translate_categories(filtered)
        fig = create_stacked_area_chart(translated)
        return fig
    except Exception as exc:
        fig = go.Figure()
        fig.add_annotation(text=f"Error processing Task 6 data: {exc}", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig


def is_task6_allowed_window() -> bool:
    return is_allowed_time()


def get_task6_summary_stats() -> dict:
    try:
        play_df = load_data()
        cleaned = clean_data(play_df)
        filtered = apply_filters(cleaned)
        summary = calculate_cumulative_installs(filtered)
        return {
            "status": "success",
            "original_rows": len(play_df),
            "cleaned_rows": len(cleaned),
            "filtered_rows": len(filtered),
            "categories": sorted(filtered["Category"].astype(str).unique().tolist()),
            "sample_months": summary["Month"].dt.strftime("%Y-%m").tolist()[:5],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    color = hex_color.lstrip("#")
    rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


if __name__ == "__main__":
    print("Task 6 module self-test")
    print(get_task6_summary_stats())
