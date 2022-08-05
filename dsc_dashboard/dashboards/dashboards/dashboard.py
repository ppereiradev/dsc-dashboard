import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from .app import app
from .apps import app_1, app_2, app_3, app_4, app_5, app_6

from data_updater.data_processing.processed_data import ProcessedData

processed_data = ProcessedData()
diretoria = processed_data.get_data_diretoria()
conectividade = processed_data.get_data_conectividade()
sistemas = processed_data.get_data_sistemas()
servicos_computacionais = processed_data.get_data_servicos_computacionais()
micro_informatica = processed_data.get_data_micro_informatica()
suporte = processed_data.get_data_suporte()

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
    server_layout = html.Div([
        dbc.Tabs([dbc.Tab(app_1.layout(diretoria), label="Diretoria STD", tab_id='tab-diretoria', tab_style={"marginLeft": "auto"}),
                  dbc.Tab(app_2.layout(conectividade), label="Conectividade", tab_id='tab-conectividade'),
                  dbc.Tab(app_3.layout(sistemas), label="Sistemas", tab_id='tab-sistemas'),
                  dbc.Tab(app_4.layout(servicos_computacionais), label="Serviços Computacionais", tab_id='tab-serv-computacionais'),
                  dbc.Tab(app_5.layout(micro_informatica), label="Micro Informática", tab_id='tab-micro'),
                  dbc.Tab(app_6.layout(suporte), label="Suporte ao Usuário", tab_id='tab-suporte'),
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
    diretoria = processed_data.get_data_diretoria()
    conectividade = processed_data.get_data_conectividade()
    sistemas = processed_data.get_data_sistemas()
    servicos_computacionais = processed_data.get_data_servicos_computacionais()
    micro_informatica = processed_data.get_data_micro_informatica()
    suporte = processed_data.get_data_suporte()
    components = [dbc.Tab(app_1.layout(diretoria), label="Diretoria STD", tab_id='tab-diretoria', tab_style={"marginLeft": "auto"}),
                  dbc.Tab(app_2.layout(conectividade), label="Conectividade", tab_id='tab-conectividade'),
                  dbc.Tab(app_3.layout(sistemas), label="Sistemas", tab_id='tab-sistemas'),
                  dbc.Tab(app_4.layout(servicos_computacionais), label="Serviços Computacionais", tab_id='tab-serv-computacionais'),
                  dbc.Tab(app_5.layout(micro_informatica), label="Micro Informática", tab_id='tab-micro'),
                  dbc.Tab(app_6.layout(suporte), label="Suporte ao Usuário", tab_id='tab-suporte'),
                  ]
    return components


app.layout = server_layout