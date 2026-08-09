from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


PLAY_DATA_PATH = Path(__file__).parent.parent / "data" / "Play Store Data.csv"
EV_DATA_PATH = Path(__file__).parent.parent / "data" / "Global EV Data 2024.csv"

# Real ISO-3 mapping for all countries present in Global EV Data 2024
COUNTRY_TO_ISO3 = {
    "Australia": "AUS", "Austria": "AUT", "Belgium": "BEL", "Brazil": "BRA",
    "Bulgaria": "BGR", "Canada": "CAN", "Chile": "CHL", "China": "CHN",
    "Colombia": "COL", "Costa Rica": "CRI", "Croatia": "HRV", "Cyprus": "CYP",
    "Czech Republic": "CZE", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN",
    "France": "FRA", "Germany": "DEU", "Greece": "GRC", "Hungary": "HUN",
    "Iceland": "ISL", "India": "IND", "Indonesia": "IDN", "Ireland": "IRL",
    "Israel": "ISR", "Italy": "ITA", "Japan": "JPN", "Korea": "KOR",
    "Latvia": "LVA", "Lithuania": "LTU", "Luxembourg": "LUX", "Mexico": "MEX",
    "Netherlands": "NLD", "New Zealand": "NZL", "Norway": "NOR", "Poland": "POL",
    "Portugal": "PRT", "Romania": "ROU", "Seychelles": "SYC", "Slovakia": "SVK",
    "Slovenia": "SVN", "South Africa": "ZAF", "Spain": "ESP", "Sweden": "SWE",
    "Switzerland": "CHE", "Thailand": "THA", "Turkiye": "TUR", "USA": "USA",
    "United Arab Emirates": "ARE", "United Kingdom": "GBR"
}


def load_play_store_top5() -> pd.DataFrame:
    """Load Play Store data, exclude A/C/G/S categories, filter Installs > 1M, return Top 5 categories."""
    df = pd.read_csv(PLAY_DATA_PATH)
    df = df.dropna(subset=["Category", "Installs"]).copy()
    df = df[df["Installs"] != "Free"]

    df["Installs"] = (
        df["Installs"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.strip()
    )
    df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce")
    df = df.dropna(subset=["Installs"])

    # Filter: exclude categories starting with A, C, G, S
    df = df[~df["Category"].str.startswith(("A", "C", "G", "S"), na=False)]

    category_summary = (
        df.groupby("Category", as_index=False)["Installs"]
        .sum()
        .sort_values("Installs", ascending=False)
    )
    top5 = category_summary[category_summary["Installs"] > 1_000_000].head(5).copy()
    top5["Highlight"] = top5["Installs"] > 1_000_000
    return top5


def load_ev_country_data() -> pd.DataFrame:
    """Extract real country geographic data from Global EV Data 2024.csv."""
    df_ev = pd.read_csv(EV_DATA_PATH)
    non_countries = ["World", "Europe", "EU27", "Rest of the world"]
    country_df = df_ev[~df_ev["region"].isin(non_countries)].copy()

    country_summary = country_df.groupby("region", as_index=False)["value"].sum()
    country_summary = country_summary.rename(columns={"region": "Country", "value": "EV_Indicator_Total"})
    country_summary["ISO3"] = country_summary["Country"].map(COUNTRY_TO_ISO3)
    return country_summary


def is_allowed_window() -> bool:
    """Return True only between 6 PM and 8 PM IST (Asia/Kolkata)."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return 18 <= now.hour < 20


def is_task2_allowed_window() -> bool:
    return is_allowed_window()


def build_figure():
    top5_apps = load_play_store_top5()
    country_data = load_ev_country_data()

    top5_str = ", ".join(top5_apps["Category"].tolist())
    total_top5_installs = top5_apps["Installs"].sum()

    # Add summary information to hover data
    country_data["Top5_App_Categories"] = top5_str
    country_data["Top5_Total_Installs"] = f"{total_top5_installs:,.0f}"

    fig = px.choropleth(
        country_data,
        locations="ISO3",
        locationmode="ISO-3",
        color="EV_Indicator_Total",
        hover_name="Country",
        hover_data={
            "ISO3": True,
            "EV_Indicator_Total": ":,.0f",
            "Top5_App_Categories": True,
            "Top5_Total_Installs": True,
        },
        color_continuous_scale="Viridis",
        title="Global Geographic Analysis (Real Country Data from Global EV 2024 & Play Store Top 5 Categories)",
        labels={
            "ISO3": "ISO Code",
            "EV_Indicator_Total": "EV Market Value",
            "Top5_App_Categories": "Top 5 App Categories",
            "Top5_Total_Installs": "Top 5 Installs Total",
        },
    )

    fig.update_layout(
        template="plotly_white",
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        height=650,
    )
    return fig


def build_task2_figure():
    return build_figure()


app = Dash(__name__)
app.title = "Global Installs & Geographic Choropleth"

app.layout = html.Div(
    style={"padding": "24px", "fontFamily": "Arial, sans-serif"},
    children=[
        html.H2("Global Installs & Country Geographic Choropleth"),
        html.P(
            "This visualization combines real country metadata from Global EV Data 2024.csv with "
            "the top 5 app categories (>1M installs, excluding A/C/G/S) from Play Store Data.csv. Available 6 PM–8 PM IST."
        ),
        html.Div(
            children=[
                dcc.Graph(figure=build_figure())
                if is_allowed_window()
                else html.Div(style={"display": "none"})
            ]
        ),
    ],
)

server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
