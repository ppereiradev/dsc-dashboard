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
processed_data.get_processed_data_all()

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
                  dbc.Tab([
                    dbc.DropdownMenu(
                        label="Geral",
                        id="dropdownmenu",
                        children=[
                            dbc.DropdownMenuItem("Geral", id="geral"),
                            dbc.DropdownMenuItem("SIG@", id="siga"),
                            dbc.DropdownMenuItem("SIGAA", id="sigaa"),
                            dbc.DropdownMenuItem("SIPAC", id="sipac"),
                            dbc.DropdownMenuItem("SIGRH", id="sigrh"),
                            dbc.DropdownMenuItem("Sistemas Diversos", id="sistemas-diversos"),
                            dbc.DropdownMenuItem("Web Sites", id="web-sites"),
                    ], right=True),
                    html.Div(app_3.layout(sistemas), id="div-sistemas")], label="Sistemas", tab_id='tab-sistemas'),

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
                  dbc.Tab([
                    dbc.DropdownMenu(
                        label="Geral",
                        id="dropdownmenu",
                        children=[
                            dbc.DropdownMenuItem("Geral", id="geral"),
                            dbc.DropdownMenuItem("SIG@", id="siga"),
                            dbc.DropdownMenuItem("SIGAA", id="sigaa"),
                            dbc.DropdownMenuItem("SIPAC", id="sipac"),
                            dbc.DropdownMenuItem("SIGRH", id="sigrh"),
                            dbc.DropdownMenuItem("Sistemas Diversos", id="sistemas-diversos"),
                            dbc.DropdownMenuItem("Web Sites", id="web-sites"),
                    ], right=True),
                    html.Div(app_3.layout(sistemas), id="div-sistemas")], label="Sistemas", tab_id='tab-sistemas'),
                  
                  dbc.Tab(app_4.layout(servicos_computacionais), label="Serviços Computacionais", tab_id='tab-serv-computacionais'),
                  dbc.Tab(app_5.layout(micro_informatica), label="Micro Informática", tab_id='tab-micro'),
                  dbc.Tab(app_6.layout(suporte), label="Suporte ao Usuário", tab_id='tab-suporte'),
                  ]
    return components


@app.callback(
    Output("div-sistemas", "children"),
    [
        Input("geral", "n_clicks"),
        Input("siga", "n_clicks"),
        Input("sigaa", "n_clicks"),
        Input("sipac", "n_clicks"),
        Input("sigrh", "n_clicks"),
        Input("sistemas-diversos", "n_clicks"),
        Input("web-sites", "n_clicks"),
    ],
)
def update_tab(geral, siga, sigaa, sipac, sigrh, sistemas_diversos, web_sites):
    
    id_lookup = {
        "geral": None,
        "siga": "SIG@",
        "sigaa": "SIGAA",
        "sipac": "SIPAC",
        "sigrh": "SIGRH",
        "sistemas-diversos": "Sistemas Diversos",
        "web-sites": "Web Sites"
    }

    ctx = dash.callback_context

    if (geral is None
            and siga is None
            and sigaa is None
            and sipac is None
            and sigrh is None
            and sistemas_diversos is None
            and web_sites is None) or not ctx.triggered:
        # if neither button has been clicked, return "Geral"
        return app_3.layout(processed_data.get_data_sistemas())

    # this gets the id of the button that triggered the callback
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return app_3.layout(processed_data.get_data_sistemas(id_lookup[button_id]))

@app.callback(
    Output("dropdownmenu", "label"),
    [
        Input("geral", "n_clicks"),
        Input("siga", "n_clicks"),
        Input("sigaa", "n_clicks"),
        Input("sipac", "n_clicks"),
        Input("sigrh", "n_clicks"),
        Input("sistemas-diversos", "n_clicks"),
        Input("web-sites", "n_clicks"),
    ],
)
def update_label(geral, siga, sigaa, sipac, sigrh, sistemas_diversos, web_sites):

    id_lookup = {
        "geral": "Geral",
        "siga": "SIG@",
        "sigaa": "SIGAA",
        "sipac": "SIPAC",
        "sigrh": "SIGRH",
        "sistemas-diversos": "Sistemas Diversos",
        "web-sites": "Web Sites"
    }

    ctx = dash.callback_context
    
    if (geral is None
            and siga is None
            and sigaa is None
            and sipac is None
            and sigrh is None
            and sistemas_diversos is None
            and web_sites is None) or not ctx.triggered:
        # if neither button has been clicked, return "Geral"
        return "Geral"

    # this gets the id of the button that triggered the callback
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return id_lookup[button_id]

app.layout = server_layout