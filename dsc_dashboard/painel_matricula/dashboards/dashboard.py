import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import os

from .app import app
from .apps import app_1
from painel_matricula.data_sigaa.sigaa import ConsultaSIGAA

consulta = ConsultaSIGAA(os.getenv("SIGAA_HOST"), 
                             os.getenv("SIGAA_DATABASE"), 
                             os.getenv("SIGAA_USER"), 
                             os.getenv("SIGAA_PASSWORD"))

matriculas = consulta.get_matriculas()

try:
    def server_layout():
        server_layout = html.Div([
                                    html.Div(children=[app_1.layout(matriculas)], id='matricula-chart'),
                                    dcc.Interval(id='interval-component',interval=10*60*1000, n_intervals=0), #10*60*1000 == minutes*seconds*milliseconds
                                ])
        return server_layout

    @app.callback(Output('matricula-chart', 'children'),[Input('interval-component', 'n_intervals')])
    def update_metrics(n_intervals):
        matriculas = consulta.get_matriculas()
        components = [
                        app_1.layout(matriculas)
                     ]
        return components

    app.layout = server_layout

except Exception:
    print("Database not ready yet...")
