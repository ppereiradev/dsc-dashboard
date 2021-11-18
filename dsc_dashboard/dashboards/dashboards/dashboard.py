import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from .app import app
from .apps import app_1, app_2, app_3

from data_updater.cleaning_data import cleaning_data

import datetime

def server_layout():
    clean_data_update = cleaning_data()
    server_layout = html.Div([
        dbc.Tabs([dbc.Tab(app_1.layout_diretoria(clean_data_update), label="Diretoria STD", tab_id='tab-diretoria', tab_style={"marginLeft": "auto"}),
                    dbc.Tab(app_2.layout_corporativas(clean_data_update), label="Soluções Corporativas", tab_id='tab-corporativas'),
                    dbc.Tab(app_3.layout_conectividade(clean_data_update), label="Conectividade", tab_id='tab-conectividade'),
                    ], active_tab="tab-diretoria", id="tabs", className='mb-3'),
        dcc.Interval(id='interval-component',interval=10*60*1000, n_intervals=0), #10*60*1000 == minutes*seconds*milliseconds
        ])
    return server_layout


@app.callback(Output('tabs', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n_intervals):
    clean_data_update = cleaning_data()
        
    components = [dbc.Tab(app_1.layout_diretoria(clean_data_update), label="Diretoria STD", tab_id='tab-diretoria', tab_style={"marginLeft": "auto"}),
                  dbc.Tab(app_2.layout_corporativas(clean_data_update), label="Soluções Corporativas", tab_id='tab-corporativas'),
                  dbc.Tab(app_3.layout_conectividade(clean_data_update), label="Conectividade", tab_id='tab-conectividade'),
                  ]
    return components


app.layout = server_layout