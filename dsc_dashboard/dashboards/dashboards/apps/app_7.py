import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

#from ..app import config_plots

import plotly.io as pio
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash

#pio.templates.default = "ggplot2"

from data_updater.cleaning_data import get_data
from dash.dependencies import Input, Output

EXTERNAL_SCRIPTS = ["https://cdnjs.cloudflare.com/ajax/libs/plotly.js/1.49.5/plotly-locale-pt-br.js"]
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
app = DjangoDash('app_7', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.UNITED, FONT_AWESOME],  external_scripts=EXTERNAL_SCRIPTS)
#server = app.server
config_plots = dict(locale='pt-br')

def charts(data):
    """
    Build the charts.

    Use the ``data`` parameter
    and use the data to build charts.

    Parameters
    ----------
    data : dict of {str : int and pd.DataFrame}
        Dictionary that contains integers and pd.DataFrames to use as
        data in the charts.

    Returns
    -------
    dict
        Dictionary of Plotly charts.
    """
    # SATISFAÇÃO
    df_satisfacao = data['df-satisfacao-suporte']
    media_satisfacao = 0.0
    for i in range(0,len(df_satisfacao.index)):
        media_satisfacao += i * df_satisfacao['qnt'][i]
    media_satisfacao = media_satisfacao/df_satisfacao['qnt'].sum()

    chart_satisfacao = px.bar(
        df_satisfacao,
        x=df_satisfacao.index,
        y='qnt',
        color_discrete_sequence=['#fcc468'],
        custom_data= np.stack((df_satisfacao.index, df_satisfacao['qnt'], df_satisfacao['percentage']))
    )

    chart_satisfacao.update_traces(
        showlegend = False,
        hovertemplate = "Nota: %{customdata[0]}<br>Qnt. de Votos: %{customdata[1]} </br>Percentual: %{customdata[2]:.2f}%"
    )

    chart_satisfacao.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    chart_satisfacao.update_layout(
        title="Satisfação dos Usuários",
        xaxis_title="Nota",
        yaxis_title='Quantidade de Votos',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),   
    )

    chart_satisfacao.add_vline(x=media_satisfacao,
                                line_width=3,
                                line_dash="dash",
                                line_color="#f17e5d",
                                annotation_text= "<sup>Fechados: " + str(data['total-fechados-suporte']) + " | </sup>"
                                                 + "<sup>Respostas: " + str(df_satisfacao['qnt'].sum()) + "</sup><br>"
                                                 + "<sup>Percentual: " + f"{(df_satisfacao['qnt'].sum()/data['total-fechados-suporte'])*100:.2f}%" + "</sup><br>"+ f"Média: {media_satisfacao:.2f}",
                                annotation_position="top",
                                annotation_font_color="#f17e5d",
                                annotation_font_size=20)

    # CHAMADOS POR ESTADO
    df_completo_estados = data['df-estados-suporte']
    
    chart_estados = go.Figure()
    chart_estados.add_trace(go.Bar(
        x=df_completo_estados.index,
        y=df_completo_estados['abertos'],
        name='Abertos',
        marker_color='#FF6353'
    ))
    chart_estados.add_trace(go.Bar(
        x=df_completo_estados.index,
        y=df_completo_estados['fechados'],
        name='Fechados',
        marker_color='lightsalmon'
    ))

    chart_estados.add_trace(go.Bar(
        x=df_completo_estados.index,
        y=df_completo_estados['acumulados'],
        name='Acumulados',
        marker_color='#FEBD11'
    ))
    
    chart_estados.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    chart_estados.update_layout(barmode='group',
                                paper_bgcolor='white',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font={'color':'#252422', "family":"Montserrat"},
                                height=350,
                                margin=dict(l=0, r=10, t=100, b=0),
                                title="Chamados por Mês",
                                xaxis_title="Mês",
                                yaxis_title='Quantidade de Chamados',
                                )

    # LEADTIME
    df_leadtime_setores = data['df-leadtime-setores']

    chart_leadtime_setores = go.Figure()
    
    chart_leadtime_setores.add_trace(go.Bar(
        x=df_leadtime_setores['mes/ano'],
        y=df_leadtime_setores['Conectividade'],
        name="CCON",
        marker_color='#FF6353'
    ))
 
    chart_leadtime_setores.add_trace(go.Bar(
        x=df_leadtime_setores['mes/ano'],
        y=df_leadtime_setores['Micro Informática'],
        name="CMI",
        marker_color='lightsalmon'
    ))

    chart_leadtime_setores.add_trace(go.Bar(
        x=df_leadtime_setores['mes/ano'],
        y=df_leadtime_setores['Serviços Computacionais'],
        name="CSC",
        marker_color='#FEBD11'
    ))

    chart_leadtime_setores.add_trace(go.Bar(
        x=df_leadtime_setores['mes/ano'],
        y=df_leadtime_setores['Sistemas'],
        name="CSIS",
    ))

    chart_leadtime_setores.add_trace(go.Bar(
        x=df_leadtime_setores['mes/ano'],
        y=df_leadtime_setores['Suporte ao Usuário'],
        name="CSUP",
    ))


    chart_leadtime_setores.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    chart_leadtime_setores.update_layout(
        barmode='group',
        title="Leadtime por Setor da STD (dias)",
        xaxis_title="Mês",
        yaxis_title='Dias',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),   
    )

    df_leadtime_bar = data['df-leadtime-suporte-bar']
    chart_leadtime_bar = go.Figure()
    
    chart_leadtime_bar.add_trace(go.Bar(
        x=df_leadtime_bar['mes/ano'],
        y=df_leadtime_bar["diff"],
        marker_color='#FF6353'
    ))
 
    chart_leadtime_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    chart_leadtime_bar.update_layout(
        barmode='group',
        title="Leadtime Médio (dias)",
        xaxis_title="Mês",
        yaxis_title='Dias',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),   
    )

    # QUANTIDADE CHAMADOS ABERTOS DIA DA SEMANA
    df_portal_semana = data['df-portal-semana']
    df_telefone_semana = data['df-telefone-semana']
    chart_qnt_semana = go.Figure()
    
    chart_qnt_semana.add_trace(go.Bar(
        x=df_portal_semana["dia"],
        y=df_portal_semana["total"],
        name='Portal',
        marker_color='#FF6353'
    ))

    chart_qnt_semana.add_trace(go.Bar(
        x=df_telefone_semana["dia"],
        y=df_telefone_semana["total"],
        name='Telefone',
        marker_color='lightsalmon'
    ))

    chart_qnt_semana.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    chart_qnt_semana.update_xaxes(categoryorder='array', categoryarray= ['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo'])
    chart_qnt_semana.update_layout(
        barmode='group',
        title="Balanço de Chamados Abertos por Dia da Semana<br><sup></sup>"
              + "<sup>Total dos Últimos 30 dias</sup>",
        xaxis_title="Dia da Semana",
        yaxis_title='Quantidade de Chamados',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),   
    )
    
    # QUANTIDADE CHAMADOS ABERTOS HORA DO DIA
    df_horas = data['df-horas']
    hours_day = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                '20', '21', '22', '23']

    chart_qnt_hora = go.Figure()
    
    chart_qnt_hora.add_trace(go.Bar(
        x=df_horas["hora"],
        y=df_horas["qnt_portal"],
        name='Portal',
        marker_color='#FF6353'
    ))

    chart_qnt_hora.add_trace(go.Bar(
        x=df_horas["hora"],
        y=df_horas["qnt_telefone"],
        name='Telefone',
        marker_color='lightsalmon'
    ))

    chart_qnt_hora.update_traces(     
        hovertemplate = "%{x}<br>Qtd.: %{y}"
    )

    chart_qnt_hora.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    chart_qnt_hora.update_xaxes(categoryorder='array', categoryarray=hours_day)
    chart_qnt_hora.update_layout(
        barmode='group',
        title="Balanço de Chamados Abertos por Hora<br><sup></sup>"
              + "<sup>Total dos Últimos 30 dias</sup>",
        xaxis_title="Hora do Dia",
        yaxis_title='Quantidade de Chamados',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),
        xaxis = dict(
            tickmode = 'array',
            tickvals = hours_day,
            ticktext = ['00hr', '01hr', '02hrs', '03hrs', '04hrs', '05hrs', '06hrs', '07hrs', '08hrs', '09hrs',
                        '10hrs', '11hrs', '12hrs', '13hrs', '14hrs', '15hrs', '16hrs', '17hrs', '18hrs', '19hrs',
                        '20hrs', '21hrs', '22hrs', '23hrs']
        )
    )

    df_leadtime_scatter = data['df-leadtime-suporte-scatter']
    chart_leadtime_scatter = px.scatter(df_leadtime_scatter, x='close_at', y='diff', color="mes/ano", labels={'mes/ano':"Mes/Ano"}, 
                                        hover_data={'close_at':False,
                                                    'diff':False,
                                                    'Aberto':df_leadtime_scatter['created_at'].dt.strftime('%d/%m/%y'),
                                                    'Fechado':df_leadtime_scatter['close_at'].dt.strftime('%d/%m/%y'),
                                                    'Dias':df_leadtime_scatter['diff'],
                            })
    
    chart_leadtime_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    chart_leadtime_scatter.update_layout(
        title="Leadtime (dias)",
        xaxis_title="Data",
        yaxis_title='Dias',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),
    )

    chart_leadtime_scatter.update_traces(marker_size=7)
    chart_leadtime_scatter.update_xaxes(tickformat="%d/%m/%Y")
    
    return {"satisfacao": chart_satisfacao,
            "estados": chart_estados,
            "leadtime-setores": chart_leadtime_setores,
            "leadtime-bar": chart_leadtime_bar,
            "abertos-qnt-semana": chart_qnt_semana,
            "abertos-qnt-hora": chart_qnt_hora,
            "leadtime-scatter": chart_leadtime_scatter,
            }

def app_content(charts, data):
    """
    Build the html components.

    Use html components with ``charts`` parameters
    to build the layout of the dashboard.

    Parameters
    ----------
    charts : dict of {str : plotly.graph_objects and plotly.express}
        Dictionary that contains the charts.
    data : dict of {str : int and pd.DataFrame}
        Dictionary that contains integers and pd.DataFrames, but the 
        integer values are used to build summary cards.

    Returns
    -------
    html.Div
        Div component of the dash_html_components.html.Div.
    """
    card_abertos_corrente = [
        dbc.CardHeader("Abertos", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="far fa-clipboard fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(data['abertos-mes-atual-suporte'],className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    card_fechados_corrente = [
        dbc.CardHeader("Fechados", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="fas fa-check-double fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(data['fechados-mes-atual-suporte'],className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    card_acumulados_corrente = [
        dbc.CardHeader("Acumulados", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="fas fa-archive fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(data['acumulados-suporte'],className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    # FIRST CHARTS CONTENT
    chart_satisfacao_dash = [
        
                dcc.Graph(figure=charts["satisfacao"],
                animate=True, config=config_plots),
    ]

    # SECOND CHARTS CONTENT
    chart_estados_dash = [
                dcc.Graph(figure=charts["estados"],
                animate=True, config=config_plots),
    ]

    # THIRD CHARTS CONTENT
    chart_leadtime_setores_dash = [
                dcc.Graph(figure=charts["leadtime-setores"],
                animate=True, config=config_plots),
    ]

    # FOURTH CHARTS CONTENT 
    chart_leadtime_bar_dash = [
                dcc.Graph(figure=charts["leadtime-bar"],
                animate=True, config=config_plots),
    ]

    # FIFTH CHARTS CONTENT
    chart_semana_dash = [
                dcc.Graph(figure=charts["abertos-qnt-semana"],
                animate=True, config=config_plots),
    ]

    # SIXTH CHARTS CONTENT
    chart_hora_dash = [
                dcc.Graph(figure=charts["abertos-qnt-hora"],
                animate=True, config=config_plots),
    ]

    # FOURTH CHARTS CONTENT
    chart_leadtime_scatter_dash = [
        
                dcc.Graph(figure=charts["leadtime-scatter"],
                animate=True, config=config_plots),
    ]

    # ROWS CONTENT
    row_1 = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(card_abertos_corrente, className='shadow cards-info cards-summary'), className='mb-4 col-lg-2 col-md-6 col-sm-6 col-xs-6 col-6'),
                    dbc.Col(dbc.Card(card_fechados_corrente, className='shadow cards-info cards-summary'), className='mb-4 col-lg-2 col-md-6 col-sm-6 col-xs-6 col-6'),
                    dbc.Col(dbc.Card(card_acumulados_corrente, className='shadow cards-info cards-summary'), className='mb-4 col-lg-2 col-md-6 col-sm-6 col-xs-6 col-6'),
                ],
                className="d-flex justify-content-center",
            ),
        ]
    )


    row_2 = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(chart_satisfacao_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_estados_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_leadtime_bar_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    
                ],
            ),
        ]
    )


    row_3 = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(chart_leadtime_scatter_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_semana_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_hora_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                ],
            ),
        ]
    )


    return html.Div([html.Div([row_1, row_2, row_3])])


def layout(data):
    """
    Build the html layout of the second tab.

    Use :func:`charts` and :func:`app_content` to fill the
    layout of the tab using Dash application components.

    Parameters
    ----------
    data : dict of {str : int and pd.DataFrame}
        Dictionary that contains integers and pd.DataFrames to use as
        data in the charts.

    Returns
    -------
    dash_html_components.html
        Html component composed of charts.
    """
    return app_content(charts(data), data)


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
    data = get_data("app_7")
    server_layout = html.Div([html.Div([
            html.A("Diretoria", href='diretoria'),
            html.A("Conectividade", href='conectividade'),
            html.A("Sistemas", href='sistemas'),
            html.A("Serviços Computacionais", href='servicos'),
            html.A("Micro Informática", href='micro'),
            html.A("Suporte ao Usuário", href='suporte', style={ "color": "#ff6353", "text-decoration": "underline"}),
        ], className="header_links"),
        html.Div(layout(data), id="app_7", className='mb-3'),
        dcc.Interval(id='interval-component',interval=10*60*1000, n_intervals=0), #10*60*1000 == minutes*seconds*milliseconds
        ])
    return server_layout

@app.callback(Output('app_7', 'children'),[Input('interval-component', 'n_intervals')])
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
    data = get_data("app_7")
    return layout(data)


app.layout = server_layout