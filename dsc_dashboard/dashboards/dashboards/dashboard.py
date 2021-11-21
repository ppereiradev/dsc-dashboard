import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from .app import app
from .apps import app_1, app_2, app_3

from data_updater.cleaning_data import get_data

def server_layout():
    """
    Build the first layout.

    Call :func:`get_data` to compute the input values 
    of the charts, then it build the layout of the 
    Dash application when it loads for the first time.

    Returns
    -------
    dash_html_components.html
        Html component composed of charts.
    """
    data = get_data()
    server_layout = html.Div([
        dbc.Tabs([dbc.Tab(app_1.layout(data), label="Diretoria STD", tab_id='tab-diretoria', tab_style={"marginLeft": "auto"}),
                    dbc.Tab(app_2.layout(data), label="Soluções Corporativas", tab_id='tab-corporativas'),
                    dbc.Tab(app_3.layout(data), label="Conectividade", tab_id='tab-conectividade'),
                    ], active_tab="tab-diretoria", id="tabs", className='mb-3'),
        dcc.Interval(id='interval-component',interval=10*60*1000, n_intervals=0), #10*60*1000 == minutes*seconds*milliseconds
        ])
    return server_layout


@app.callback(Output('tabs', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n_intervals):
    """
    Build the updated layout.

    Be a callback function triggered by the ``dcc.Interval`` component,
    then call :func:`get_data` to compute the input values of the 
    charts, and build the updated layout of the Dash application.

    Parameters
    ----------
    n_intervals : int
        Value that represents how many updates have been happend
        already, it is not used.

    Returns
    -------
    list of dbc.Tabs
        Return a list of dbc.Tabs components to insert on html.Div.
    """
    data = get_data()
    components = [dbc.Tab(app_1.layout(data), label="Diretoria STD", tab_id='tab-diretoria', tab_style={"marginLeft": "auto"}),
                  dbc.Tab(app_2.layout(data), label="Soluções Corporativas", tab_id='tab-corporativas'),
                  dbc.Tab(app_3.layout(data), label="Conectividade", tab_id='tab-conectividade'),
                  ]
    return components


app.layout = server_layout