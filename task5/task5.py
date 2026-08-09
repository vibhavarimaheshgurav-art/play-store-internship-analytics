
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px


PLAY_DATA_PATH = Path(__file__).parent.parent / "data" / "Play Store Data.csv"
REVIEWS_PATH = Path(__file__).parent.parent / "data" / "User Reviews.csv"


def load_data():
    """Load both Play Store and User Reviews datasets.

    Returns a tuple (play_df, reviews_df)
    """
    play_df = pd.read_csv(PLAY_DATA_PATH)
    reviews_df = pd.read_csv(REVIEWS_PATH)
    return play_df, reviews_df


def _convert_size_to_mb(size_str):
    if pd.isna(size_str):
        return None
    s = str(size_str).strip()
    if s in ["Varies with device", "", "nan"]:
        return None
    try:
        if s.endswith("M"):
            return float(s[:-1])
        if s.endswith("k"):
            return float(s[:-1]) / 1024
        # fallback: try numeric
        return float(s)
    except Exception:
        return None


def clean_data(play_df: pd.DataFrame, reviews_df: pd.DataFrame):
    """Clean both datasets and prepare for merging.

    Returns cleaned copies (play, reviews)
    """
    play = play_df.copy()
    reviews = reviews_df.copy()

    play = play.drop_duplicates()
    required_play_cols = {"App", "Size", "Installs", "Rating", "Reviews", "Category"}
    missing = required_play_cols - set(play.columns)
    if missing:
        raise ValueError(f"Play Store dataset missing columns: {missing}")

    play["Installs"] = (
        play["Installs"].astype(str).str.replace(",", "", regex=False).str.replace("+", "", regex=False).str.strip()
    )
    play["Installs"] = pd.to_numeric(play["Installs"], errors="coerce")
    play["Size_MB"] = play["Size"].apply(_convert_size_to_mb)
    play["Rating"] = pd.to_numeric(play["Rating"], errors="coerce")
    play["Reviews"] = pd.to_numeric(play["Reviews"], errors="coerce")
    play = play.dropna(subset=["Installs", "Size_MB", "Rating", "Reviews", "App", "Category"]).copy()

    required_rev_cols = {"App", "Sentiment_Subjectivity"}
    missing_r = required_rev_cols - set(reviews.columns)
    if missing_r:
        raise ValueError(f"User Reviews dataset missing columns: {missing_r}")

    reviews = reviews.drop_duplicates()
    reviews = reviews[["App", "Sentiment_Subjectivity"]].copy()
    reviews["Sentiment_Subjectivity"] = pd.to_numeric(reviews["Sentiment_Subjectivity"], errors="coerce")

    return play, reviews


def merge_datasets(play: pd.DataFrame, reviews: pd.DataFrame):
    """Merge reviews with play data on `App`. Aggregate reviews by app (mean subjectivity)."""
    rev_agg = (
        reviews.groupby("App", as_index=False)["Sentiment_Subjectivity"].mean()
    )
    merged = pd.merge(play, rev_agg, on="App", how="left")
    return merged


def apply_filters(df: pd.DataFrame):
    """Apply the filters specified in Task 5."""
    df = df.copy()

    allowed = {"GAME", "BEAUTY", "BUSINESS", "COMICS", "COMMUNICATION", "DATING", "ENTERTAINMENT", "SOCIAL", "EVENTS"}
    df = df[df["Category"].astype(str).str.upper().isin(allowed)]
    df = df[~df["App"].astype(str).str.contains("[Ss]", regex=True, na=False)]
    df = df[df["Rating"] > 3.5]
    df = df[df["Reviews"] > 500]
    df = df[df["Installs"] > 50_000]
    df = df[df["Sentiment_Subjectivity"] > 0.5]

    return df


def translate_categories(df: pd.DataFrame):
    """Return a copy with a display label for Category (translated labels only for display)."""
    df = df.copy()
    mapping = {
        "BEAUTY": "सौंदर्य",
        "BUSINESS": "வணிகம்",
        "DATING": "Partnersuche",
    }
    # Create display column
    def map_label(cat):
        if pd.isna(cat):
            return cat
        up = str(cat).upper()
        return mapping.get(up, cat)

    df["Category_Display"] = df["Category"].apply(map_label)
    return df


def create_bubble_chart(df: pd.DataFrame):
    """Create interactive Plotly bubble chart per requirements."""
    if df.empty:
        fig = px.scatter()
        fig.add_annotation(text="No data available after applying filters.", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    df = df.copy()
    if "Category_Display" not in df.columns:
        df = translate_categories(df)
    df["Category_Upper"] = df["Category"].astype(str).str.upper()

    categories_in_df = df["Category_Upper"].unique()
    color_map = {cat: ("#FF69B4" if cat == "GAME" else "#B0BEC5") for cat in categories_in_df}

    fig = px.scatter(
        df,
        x="Size_MB",
        y="Rating",
        size="Installs",
        color="Category_Upper",
        hover_name="App",
        hover_data={"Size_MB": ":.2f", "Rating": ":.2f", "Installs": ":,", "Category_Display": True},
        title="App Size vs Rating (Bubble size = Installs)",
        labels={"Size_MB": "Size (MB)", "Rating": "Average Rating", "Category_Upper": "Category"},
        color_discrete_map=color_map,
    )

    fig.update_layout(template="plotly_white", legend_title_text="Category", height=650, autosize=True)
    fig.update_traces(marker=dict(sizemode="area", sizeref=2.*max(df["Installs"]) / (100**2), line_width=0.5))
    return fig


def is_task5_allowed_window() -> bool:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return 17 <= now.hour < 19


def build_task5_figure():
    try:
        play, reviews = load_data()
        play_c, reviews_c = clean_data(play, reviews)
        merged = merge_datasets(play_c, reviews_c)
        filtered = apply_filters(merged)
        translated = translate_categories(filtered)
        fig = create_bubble_chart(translated)
        return fig
    except Exception as exc:
        fig = px.scatter()
        fig.add_annotation(text=f"Error processing Task 5 data: {exc}", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig


def get_task5_summary_stats():
    try:
        play, reviews = load_data()
        play_c, reviews_c = clean_data(play, reviews)
        merged = merge_datasets(play_c, reviews_c)
        filtered = apply_filters(merged)
        return {
            "status": "success",
            "original_rows": len(play),
            "merged_rows": len(merged),
            "filtered_rows": len(filtered),
            "categories": sorted(filtered["Category"].astype(str).unique().tolist()),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


if __name__ == "__main__":
    print("Task 5 module self-test")
    print(get_task5_summary_stats())
