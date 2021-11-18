import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from ..app import app, config_plots

def layout_conectividade(clean_data):

    ''' FIGURES CHARTS '''

    ######### SATISFACAO GRÁFICO #########
    df_satisfacao = clean_data['df-satisfacao']
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
        title="Satisfação dos Usuários<br><sup></sup>"
              "<sup>Total Fechados: " + str(clean_data['total-fechados']) + " | </sup>"
              + "<sup>Total Respostas: " + str(df_satisfacao['qnt'].sum()) + "</sup><br>"
              + "<sup>Percentual de Respostas: " + f"{(df_satisfacao['qnt'].sum()/clean_data['total-fechados'])*100:.2f}%" + "</sup>",
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
                                annotation_text=f"Média: {media_satisfacao:.2f}",
                                annotation_position="top",
                                annotation_font_color="#f17e5d",
                                annotation_font_size=20)

    ######### END SATISFACAO GRÁFICO #########

    
    ######### CHAMADOS POR ESTADO GRÁFICO #########
    df_completo_estados = clean_data['df-estados']
    
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
                                height=400,
                                margin=dict(l=0, r=10, t=100, b=0),
                                title="Chamados por Mês",
                                xaxis_title="Mês",
                                yaxis_title='Quantidade de Chamados',
                                )

    #chart_leadtime_std = px.bar(df_joined, x=df_joined['categoria'].value_counts().index, y=df_joined['categoria'].value_counts())

    """ chart_leadtime_std.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422'},
        height=400,
        margin=dict(l=0, r=10, t=10, b=0),
        
        legend_title_text='Estado:',
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ))
 """
    ######### END CHAMADOS POR ESTADO GRÁFICO #########

    ######### LEADTIME GRÁFICO #########

    df_leadtime_setores = clean_data['df-leadtime-setores']

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
        xaxis_title="Setor",
        yaxis_title='Dias',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=400,
        margin=dict(l=0, r=10, t=100, b=0),   
    )


    """ 
    chart_leadtime_setores.update_traces(
        showlegend = False,
        hovertemplate = "Setor: %{customdata[0]}<br>Leadtime: %{customdata[1]:.0f} dias"
    )
    
    chart_leadtime_setores.add_hline(y=df_leadtime_setores['diff'].mean(),
                                line_width=3,
                                line_dash="dash",
                                line_color="yellow",
                                annotation_text=f"Média: {df_leadtime_setores['diff'].mean():.2f}",
                                annotation_position="top",
                                annotation_font_color="yellow",
                                annotation_font_size=20)
    """





    df_leadtime_unidades = clean_data['df-leadtime-unidades']
    chart_leadtime_unidades = go.Figure()
    
    chart_leadtime_unidades.add_trace(go.Bar(
        x=df_leadtime_unidades['mes/ano'],
        y=df_leadtime_unidades["CODAI"],
        name='CODAI',
        marker_color='#FF6353'
    ))
 
    chart_leadtime_unidades.add_trace(go.Bar(
        x=df_leadtime_unidades['mes/ano'],
        y=df_leadtime_unidades["UABJ"],
        name='UABJ',
        marker_color='lightsalmon'
    ))

    chart_leadtime_unidades.add_trace(go.Bar(
        x=df_leadtime_unidades['mes/ano'],
        y=df_leadtime_unidades["UAST"],
        name='UAST',
        marker_color='#FEBD11'
    ))

    chart_leadtime_unidades.add_trace(go.Bar(
        x=df_leadtime_unidades['mes/ano'],
        y=df_leadtime_unidades["UACSA"],
        name='UACSA',
    ))

    chart_leadtime_unidades.add_trace(go.Bar(
        x=df_leadtime_unidades['mes/ano'],
        y=df_leadtime_unidades["UAEADTec"],
        name="UAEADTec",
    ))


    chart_leadtime_unidades.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    chart_leadtime_unidades.update_layout(
        barmode='group',
        title="Leadtime por Unidade Acadêmica (dias)",
        xaxis_title="Unidade",
        yaxis_title='Dias',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=400,
        margin=dict(l=0, r=10, t=100, b=0),   
    )


    ######### END LEADTIME GRÁFICO #########


    ''' SUMMARY CARDS' CONTENT '''
    card_abertos_corrente = [
        dbc.CardHeader("Abertos", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="far fa-clipboard fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(clean_data['abertos-mes-atual'],className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    card_fechados_corrente = [
        dbc.CardHeader("Fechados", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="fas fa-check-double fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(clean_data['fechados-mes-atual'],className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    card_acumulados_corrente = [
        dbc.CardHeader("Acumulados", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="fas fa-archive fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(clean_data['acumulados'],className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]


    ''' FIRST CHARTS CONTENT '''
    chart_satisfacao_dash = [
        
                dcc.Graph(figure=chart_satisfacao,
                animate=True, config=config_plots),
    ]

    ''' SECOND CHARTS CONTENT '''
    chart_estados_dash = [
        
                dcc.Graph(figure=chart_estados,
                animate=True, config=config_plots),
    ]

    ''' THIRD CHARTS CONTENT '''
    chart_leadtime_setores_dash = [
        
                dcc.Graph(figure=chart_leadtime_setores,
                animate=True, config=config_plots),
    ]

    ''' FOURTH CHARTS CONTENT '''
    chart_leadtime_unidades_dash = [
        
                dcc.Graph(figure=chart_leadtime_unidades,
                animate=True, config=config_plots),
    ]



    ''' ROWS CONTENT '''
    row_1 = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col([dbc.Card(card_abertos_corrente, className='shadow cards-info cards-summary mb-4'),
                            dbc.Card(card_fechados_corrente, className='shadow cards-info cards-summary mb-4'),
                            dbc.Card(card_acumulados_corrente, className='shadow cards-info cards-summary mb-4')], className='first-col mb-4 col-lg-2 col-md-12 col-sm-12 col-xs-12 col-12'),

                    dbc.Col([dbc.Card(chart_satisfacao_dash, className='shadow cards-info mb-4'),
                            dbc.Card(chart_leadtime_setores_dash, className='shadow cards-info mb-4')], className='mb-4 col-lg-5 col-md-12 col-sm-12 col-xs-12 col-12'),

                    dbc.Col([dbc.Card(chart_estados_dash, className='shadow cards-info mb-4'),
                            dbc.Card(chart_leadtime_unidades_dash, className='shadow cards-info mb-4')], className='mb-4 col-lg-5 col-md-12 col-sm-12 col-xs-12 col-12'),
                ],
                className="mb-4",
            ),
        ]
    )


    ''' END CHART CARDS' CONTENT '''
    ##############################

    ''' final layout render '''
    layout = html.Div([html.Div([row_1])])

    return layout