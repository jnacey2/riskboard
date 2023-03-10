# Data manipulation libraries
import numpy as np
import pandas as pd
import boto3
import s3fs

# Dashboard-related libraries
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_auth
from dash import dash_table


# Data visualization libraries
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

dash.register_page(__name__, path="/", order=1)




def serve_layout():
    macro_df = pd.read_csv("https://nacey-capstone.s3.amazonaws.com/macro_dash.csv")
    macro_df["BBB OAS"] = macro_df["BBB OAS"] * 100
    macro_df["CCC OAS"] = macro_df["CCC OAS"] * 100
    macro_df["BB OAS"] = macro_df["BB OAS"] * 100
    macro_df["B OAS"] = macro_df["B OAS"] * 100
    macro_df["BAML IG OAS"] = macro_df["BAML IG OAS"] * 100
    macro_df["BAML HY OAS"] = macro_df["BAML HY OAS"] * 100

    std_df = macro_df.drop(["Unnamed: 0"], axis=1).diff(5).describe().T["std"]


    def dashboard_tables(main_df, names, std_df=std_df):
        df = pd.DataFrame(index=names, columns=["Level", "1Wk Δ", "1Wk Std"])

        for name in names:
            df.loc[name]["Level"] = main_df[name].tail(1).item()

        for name in names:
            df.loc[name]["1Wk Δ"] = (
                df.loc[name]["Level"] - main_df[name][:-5].tail(1).item()
            )

        for name in names:
            df.loc[name]["1Wk Std"] = std_df.loc[name]

        df["Δ Z-Score"] = df["1Wk Δ"] / df["1Wk Std"]

        df.reset_index(inplace=True)
        df["Level"] = df["Level"].astype(float).round(decimals=3)
        df["1Wk Δ"] = df["1Wk Δ"].astype(float).round(decimals=3)
        df["1Wk Std"] = df["1Wk Std"].astype(float).round(decimals=3)
        df["Δ Z-Score"] = df["Δ Z-Score"].astype(float).round(decimals=3)

        df = df.drop("1Wk Std", axis=1)

        df = df.rename(columns={"index": ""})

        return df


    # Rates Tables
    treas_rates_table = dashboard_tables(
        macro_df, ["2yTreas", "5yTreas", "10yTreas", "30yTreas", "30yr Mortgage"]
    )
    curve_rates_table = dashboard_tables(macro_df, ["2s10s", "2s30s", "5s30s"])
    ilbe_rates_table = dashboard_tables(macro_df, ["5y5yILBE", "5yrReal"])

    # Equity Tables
    equity_indices_table = dashboard_tables(
        macro_df,
        [
            "SPX",
            "NASDAQ",
            "Russell",
            "FTSE",
            "DAX",
            "CAC40",
            "Nikkei",
            "Shenzen",
            "Hang Seng",
        ],
    )

    vol_table = dashboard_tables(macro_df, ["VIX", "VVIX", "VXN"])

    # US Credit Tables
    baml_rates_table = dashboard_tables(macro_df, ["BAML IG OAS", "BAML HY OAS"])
    corp_rates_table = dashboard_tables(macro_df, ["BBB OAS", "BB OAS", "B OAS", "CCC OAS"])

    # FX Table
    currency_table = dashboard_tables(
        macro_df, ["EURUSD", "USDGBP", "CHFUSD", "USDJPY", "CADUSD", "MXNUSD", "USDYUAN"]
    )

    # Commodity Table
    commodities_table = dashboard_tables(macro_df, ["Copper", "Gold"])

    layout = html.Div(
        children=[
            html.P(),
            dbc.Row(
                html.Center(html.H3("Volatility-Adjusted Macro Dashboard")),
            ),
            html.Hr(),
            html.Center(
                html.Div(
                    """The Volatility-Adjusted Macro Dasboard displays macroeconomic variables relevant to market 
                                        returns.  We hightlight current levels, week over week change, and the z-score of that change
                                        so users can quickly see outsized changes relative to their historical distribution."""
                )
            ),
            html.P(" "),
            html.P(" "),
            html.Center(html.Div([
                dbc.RadioItems(
                        id="radios",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                        options=[
                            {"label": "1D", "value": 1},
                            {"label": "2D", "value": 2},
                            {"label": "3D", "value": 3},
                            {"label": "5D", "value": 4},
                            {"label": "10D", "value": 5},
                            {"label": "1M", "value": 6},
                            {"label": "2M", "value": 7},
                            {"label": "3M", "value": 8},
                            {"label": "6M", "value": 9},
                            {"label": "1Y", "value": 10},
                        ],
                    value=1,),
                html.Div(id="output"),
            ],
            className="radio-group")),
            html.P(" "),
            dbc.Row(
                children=[
                    dbc.Col(children=[html.Center(html.Div("Rates"))], width=3),
                    dbc.Col(children=[html.Center(html.Div("Equities"))], width=3),
                    dbc.Col(children=[html.Center(html.Div("Credit"))], width=3),
                    dbc.Col(children=[html.Center(html.Div("Global"))], width=3),
                ]
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            html.Center(html.Div("US Treasuries")),
                            html.P(),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i}
                                    for i in treas_rates_table.columns
                                ],
                                data=treas_rates_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                ],
                            ),
                            html.P(),
                            html.Center(html.P("US Treasury Curve")),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i}
                                    for i in curve_rates_table.columns
                                ],
                                data=curve_rates_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                ],
                            ),
                            html.P(),
                            html.Center(html.P("Inflation & Real Rates")),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i}
                                    for i in ilbe_rates_table.columns
                                ],
                                data=ilbe_rates_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                ],
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        children=[
                            html.Center(html.Div("Global")),
                            html.P(),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i}
                                    for i in equity_indices_table.columns
                                ],
                                data=equity_indices_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                ],
                            ),
                            html.P(),
                            html.Center(html.P("Volatility")),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i} for i in vol_table.columns
                                ],
                                data=vol_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                ],
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        children=[
                            html.Center(html.Div("US")),
                            html.P(),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i}
                                    for i in baml_rates_table.columns
                                ],
                                data=baml_rates_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                ],
                            ),
                            html.P(),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i}
                                    for i in corp_rates_table.columns
                                ],
                                data=corp_rates_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                ],
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        children=[
                            html.Center(html.Div("FX")),
                            html.P(),
                            html.P(),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i} for i in currency_table.columns
                                ],
                                data=currency_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                ],
                            ),
                            html.P(),
                            html.Center(html.P("Commodities")),
                            dash_table.DataTable(
                                columns=[
                                    {"name": i, "id": i}
                                    for i in commodities_table.columns
                                ],
                                data=commodities_table.to_dict("records"),
                                style_cell=dict(
                                    textAlign="right",
                                    font_family="sans-serif",
                                    padding="3px",
                                    border="none",
                                ),
                                style_header=dict(
                                    backgroundColor="#005999",
                                    font_family="sans-serif",
                                    color="white",
                                    size=16,
                                    border="none",
                                ),
                                style_data=dict(
                                    backgroundColor="#4e5d6c",
                                    font_family="sans-serif",
                                    color="white",
                                    border="none",
                                ),
                                style_data_conditional=[
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 1 && {Δ Z-Score} < 2",
                                        },
                                        "backgroundColor": "lightgreen",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} > 2",
                                        },
                                        "backgroundColor": "green",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -1 && {Δ Z-Score} > -2",
                                        },
                                        "backgroundColor": "tomato",
                                    },
                                    {
                                        "if": {
                                            "column_id": "Δ Z-Score",
                                            "filter_query": "{Δ Z-Score} < -2",
                                        },
                                        "backgroundColor": "red",
                                    },
                                ],
                            ),
                        ],
                        width=3,
                    ),
                ]
            ),
        ]
    )

    return layout


layout = serve_layout