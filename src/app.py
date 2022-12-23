# Data manipulation libraries
import numpy as np
import pandas as pd

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


USERNAME_PASSWORD_PAIRS = [['root', 'root']]

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "padding": "2rem 1rem",
    #"background-color": "#f8f9fa",
    "color": "white"
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

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


######################
### BEGIN APP LAYOUT #
######################

app = dash.Dash(external_stylesheets=[dbc.themes.SUPERHERO],
                use_pages=True,
                suppress_callback_exceptions=True)
app.title = "riskboard"
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server

# Sidebar implemention

def serve_layout():

    sidebar = html.Div([
            html.H2("riskboard", className="display-4"),
            html.Hr(),
            dbc.Nav([
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("Market Data", href="/market-data", active="exact"),
                    dbc.NavLink("Index Analytics", href="/indices", active="exact"),
                    dbc.NavLink("Equity Analytics", href="/credit-main", active="exact"),
                    dbc.NavLink("Statistical Arbitrage", href="/stat-arb", active="exact"),
                    dbc.NavLink("Crypto Analytics", href="/crypto-main", active="exact"),
                    dbc.NavLink("Economic Data", href="/econ-main", active="exact")],
                vertical=True,
                pills=True)],
        style=SIDEBAR_STYLE,)

    content = html.Div(id="page-content", style=CONTENT_STYLE)

    layout = html.Div([dcc.Location(id="url"), sidebar, content])

    return layout

app.layout = serve_layout    

if __name__ == "__main__":
    app.run_server(debug=True)