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


# Data visualization libraries
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

TABS_STYLES = {
    'height': '44px'
}
TAB_STYLE = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'backgroundColor': '#787878'
}

TAB_SELECTED_STYLE = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

dash.register_page(
    __name__,
    order=2,
    title='Market Data',
    name='Market Data'
)

def serve_layout():
    layout = html.Div(children=[
        html.Br(),
        html.Div(children=[
            html.Center(html.H2('Market Data')),
            html.Hr(),
            html.Div(children=[
                dcc.Tabs(children=[
                    dcc.Tab(id='rates-tab', label='Rates Markets', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(id='credit-tab', label='Credit Markets', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(id='vol-tab', label='Volatility Markets', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(id='commodity-tab', label='Commodity Markets', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                    dcc.Tab(id='econ-tab', label='Economic Data', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),

                ])
            ])
        ])
    ])

    return layout

layout = serve_layout