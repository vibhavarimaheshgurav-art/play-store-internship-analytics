"""Integrated Dash dashboard with the original choropleth, Task 3, and Task 4 views."""

import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc, html

from task2.task2 import build_task2_figure, is_task2_allowed_window
from task3.task3 import build_task3_figure, get_task3_summary_stats, is_task3_allowed_window
from task4.task4 import build_task4_figure, get_task4_summary_stats, is_task4_allowed_window
from task5.task5 import build_task5_figure, get_task5_summary_stats, is_task5_allowed_window
from task6.task6 import build_task6_figure, get_task6_summary_stats, is_task6_allowed_window





app = Dash(__name__)
app.title = "Play Store Analytics Dashboard"


def create_task3_section():
    """Create the Task 3 visualization section."""
    return html.Div(
        style={
            "padding": "24px",
            "backgroundColor": "#f5f7fa",
            "borderRadius": "8px",
            "marginTop": "40px",
            "border": "1px solid #e0e6ed",
        },
        children=[
            html.H2("Task 3: Free vs Paid Apps Analysis", style={"marginTop": "0"}),
            html.P(
                "Dual-axis chart comparing Average Installs and Average Revenue for Free vs. Paid apps across the Top 3 app categories.",
                style={"color": "#666", "fontSize": "14px"},
            ),
            html.Div(id="task3-content", style={"minHeight": "650px"}),
            html.Div(
                id="task3-stats",
                style={
                    "marginTop": "20px",
                    "padding": "15px",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "6px",
                    "fontSize": "13px",
                    "color": "#555",
                },
            ),
        ],
    )


def create_task4_section():
    """Create the Task 4 visualization section."""
    return html.Div(
        style={
            "padding": "24px",
            "backgroundColor": "#f5f7fa",
            "borderRadius": "8px",
            "marginTop": "40px",
            "border": "1px solid #e0e6ed",
        },
        children=[
            html.H2("Task 4: Monthly Installs Trend by Category", style={"marginTop": "0"}),
            html.P(
                "Interactive time-series chart showing monthly total installs for selected categories with growth shading.",
                style={"color": "#666", "fontSize": "14px"},
            ),
            html.Div(id="task4-content", style={"minHeight": "650px"}),
            html.Div(
                id="task4-stats",
                style={
                    "marginTop": "20px",
                    "padding": "15px",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "6px",
                    "fontSize": "13px",
                    "color": "#555",
                },
            ),
        ],
    )


app.layout = html.Div(
    style={
        "padding": "24px",
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#ffffff",
        "minHeight": "100vh",
    },
    children=[
        html.Div(
            style={"maxWidth": "1200px", "margin": "0 auto"},
            children=[
                html.H1(
                    "Play Store Analytics Dashboard",
                    style={"textAlign": "center", "color": "#333", "marginBottom": "10px", "fontSize": "32px"},
                ),
                html.P(
                    "Interactive visualizations based on Google Play Store dataset",
                    style={"textAlign": "center", "color": "#888", "marginBottom": "30px", "fontSize": "14px"},
                ),
                html.Hr(style={"borderColor": "#e0e6ed", "marginBottom": "30px"}),
                html.Div(
                    style={
                        "padding": "24px",
                        "backgroundColor": "#f5f7fa",
                        "borderRadius": "8px",
                        "border": "1px solid #e0e6ed",
                        "marginBottom": "30px",
                    },
                    children=[
                        html.H2("Global Installs by Category", style={"marginTop": "0"}),
                        html.P(
                            "This choropleth visualization combines real country metadata from Global EV Data 2024 with top app categories from Play Store Data. Available 6 PM to 8 PM IST.",
                            style={"color": "#666", "fontSize": "14px"},
                        ),
                        html.Div(id="choropleth-content", style={"minHeight": "650px"}),
                    ],
                ),
                create_task3_section(),
                create_task4_section(),
                # Task 5 section
                html.Div(
                    style={
                        "padding": "24px",
                        "backgroundColor": "#f5f7fa",
                        "borderRadius": "8px",
                        "marginTop": "40px",
                        "border": "1px solid #e0e6ed",
                    },
                    children=[
                        html.H2("Task 5: Size vs Rating Bubble Chart", style={"marginTop": "0"}),
                        html.P(
                            "Interactive bubble chart showing Size (MB) vs Average Rating with bubble size = Installs. Available 5 PM to 7 PM IST.",
                            style={"color": "#666", "fontSize": "14px"},
                        ),
                        html.Div(id="task5-content", style={"minHeight": "650px"}),
                        html.Div(
                            id="task5-stats",
                            style={
                                "marginTop": "20px",
                                "padding": "15px",
                                "backgroundColor": "#ffffff",
                                "borderRadius": "6px",
                                "fontSize": "13px",
                                "color": "#555",
                            },
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "padding": "24px",
                        "backgroundColor": "#f5f7fa",
                        "borderRadius": "8px",
                        "marginTop": "40px",
                        "border": "1px solid #e0e6ed",
                    },
                    children=[
                        html.H2("Task 6: Cumulative Installs by Category", style={"marginTop": "0"}),
                        html.P(
                            "Interactive stacked area chart showing cumulative installs over time for selected categories. Available 4 PM to 6 PM IST.",
                            style={"color": "#666", "fontSize": "14px"},
                        ),
                        html.Div(id="task6-content", style={"minHeight": "650px"}),
                        html.Div(
                            id="task6-stats",
                            style={
                                "marginTop": "20px",
                                "padding": "15px",
                                "backgroundColor": "#ffffff",
                                "borderRadius": "6px",
                                "fontSize": "13px",
                                "color": "#555",
                            },
                        ),
                    ],
                ),
                html.Hr(style={"marginTop": "40px", "borderColor": "#e0e6ed"}),
                html.Div(
                    style={"textAlign": "center", "color": "#999", "fontSize": "12px", "padding": "20px"},
                    children=[html.P("Dataset: Google Play Store (10,841+ apps) | Last Updated: 2024")],
                ),
            ],
        ),
        dcc.Interval(id="interval-component", interval=60000, n_intervals=0),
    ],
)


@callback(Output("choropleth-content", "children"), Input("interval-component", "n_intervals"))
def update_choropleth(_):
    """Update choropleth chart based on time window."""
    if is_task2_allowed_window():
        return dcc.Graph(figure=build_task2_figure())

    return html.Div(style={"display": "none"})


@callback([Output("task3-content", "children"), Output("task3-stats", "children")], Input("interval-component", "n_intervals"))
def update_task3(_):
    """Update Task 3 chart based on time window."""
    if is_task3_allowed_window():
        chart_content = dcc.Graph(figure=build_task3_figure())
        stats = get_task3_summary_stats()
        if stats.get("status") == "success":
            stats_html = html.Div(
                children=[
                    html.Strong("Summary Statistics:", style={"display": "block", "marginBottom": "8px"}),
                    html.P(f"Original rows: {stats['original_rows']} | Filtered rows: {stats['filtered_rows']}"),
                    html.P(f"Free apps: {stats['free_apps']} | Paid apps: {stats['paid_apps']}"),
                    html.P(f"Top 3 categories: {', '.join(stats['top_3_categories'])}"),
                ]
            )
        else:
            stats_html = html.P(f"Error: {stats.get('message', 'Unknown error')}", style={"color": "red"})
        return chart_content, stats_html

    return html.Div(style={"display": "none"}), html.Div(style={"display": "none"})


@callback([Output("task4-content", "children"), Output("task4-stats", "children")], Input("interval-component", "n_intervals"))
def update_task4(_):
    """Update Task 4 chart based on the required IST time window."""
    if is_task4_allowed_window():
        chart_content = dcc.Graph(figure=build_task4_figure())
        stats = get_task4_summary_stats()
        if stats.get("status") == "success":
            stats_html = html.Div(
                children=[
                    html.Strong("Filter Summary:", style={"display": "block", "marginBottom": "8px"}),
                    html.P(f"Rows after filtering: {stats['rows_after_filter']}"),
                    html.P(f"Categories: {', '.join(stats['categories'])}"),
                ]
            )
        else:
            stats_html = html.P(f"Error: {stats.get('message', 'Unknown error')}", style={"color": "red"})
        return chart_content, stats_html

    return html.Div(style={"display": "none"}), html.Div(style={"display": "none"})


@callback([Output("task5-content", "children"), Output("task5-stats", "children")], Input("interval-component", "n_intervals"))
def update_task5(_):
    """Update Task 5 bubble chart based on 5 PM-7 PM IST window."""
    if is_task5_allowed_window():
        chart_content = dcc.Graph(figure=build_task5_figure())
        stats = get_task5_summary_stats()
        if stats.get("status") == "success":
            stats_html = html.Div(
                children=[
                    html.Strong("Filter Summary:", style={"display": "block", "marginBottom": "8px"}),
                    html.P(f"Original rows: {stats.get('original_rows', 'N/A')} | Merged rows: {stats.get('merged_rows', 'N/A')}") ,
                    html.P(f"Rows after filter: {stats.get('filtered_rows', 0)}"),
                    html.P(f"Categories: {', '.join(stats.get('categories', []))}"),
                ]
            )
        else:
            stats_html = html.P(f"Error: {stats.get('message', 'Unknown error')}", style={"color": "red"})
        return chart_content, stats_html

    return html.Div(style={"display": "none"}), html.Div(style={"display": "none"})


@callback([Output("task6-content", "children"), Output("task6-stats", "children")], Input("interval-component", "n_intervals"))
def update_task6(_):
    """Update Task 6 chart based on the required 4 PM-6 PM IST window."""
    if is_task6_allowed_window():
        chart_content = dcc.Graph(figure=build_task6_figure())
        stats = get_task6_summary_stats()
        if stats.get("status") == "success":
            stats_html = html.Div(
                children=[
                    html.Strong("Filter Summary:", style={"display": "block", "marginBottom": "8px"}),
                    html.P(f"Original rows: {stats.get('original_rows', 'N/A')} | Cleaned rows: {stats.get('cleaned_rows', 'N/A')}"),
                    html.P(f"Rows after filter: {stats.get('filtered_rows', 0)}"),
                    html.P(f"Categories: {', '.join(stats.get('categories', []))}"),
                ]
            )
        else:
            stats_html = html.P(f"Error: {stats.get('message', 'Unknown error')}", style={"color": "red"})
        return chart_content, stats_html

    return html.Div(style={"display": "none"}), html.Div(style={"display": "none"})


server = app.server


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)
