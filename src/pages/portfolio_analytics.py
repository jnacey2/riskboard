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

dash.register_page(
    __name__,
    order=6,
    title='Portfolio Analytics',
    name='Portfolio Analytics'
)

layout = html.Div('This is the Portfolio Analytics Page')