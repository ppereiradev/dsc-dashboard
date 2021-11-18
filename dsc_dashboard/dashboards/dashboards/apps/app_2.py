import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from ..app import app, config_plots


def layout_corporativas(clean_data):

    ##################################################################################################################
    ##################################################################################################################
    ##########                                                                                              ##########
    ##########                                           CHARTS                                             ##########
    ##########                                                                                              ##########
    ##################################################################################################################
    ##################################################################################################################
  
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
                                height=350,
                                margin=dict(l=0, r=10, t=100, b=0),
                                title="Chamados por Mês",
                                xaxis_title="Mês",
                                yaxis_title='Quantidade de Chamados',
                                )


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
        height=350,
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
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),   
    )


    ######### END LEADTIME GRÁFICO #########

    ######################## QUANTIDADE CHAMADOS ABERTOS DIA DA SEMANA ##############################################
    df_portal_semana = clean_data['df-portal-semana']
    df_telefone_semana = clean_data['df-telefone-semana']
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
    ######################## END QUANTIDADE CHAMADOS ABERTOS DIA DA SEMANA ##############################################

    ######################## QUANTIDADE CHAMADOS ABERTOS HORA DO DIA ##############################################
    df_horas = clean_data['df-horas']
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
    ######################## END QUANTIDADE CHAMADOS ABERTOS HORA DO DIA ##############################################

    ##################################################################################################################
    ##################################################################################################################
    ##########                                                                                              ##########
    ##########                                      APPLICATION                                             ##########
    ##########                                                                                              ##########
    ##################################################################################################################
    ##################################################################################################################

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

    ''' FIFTH CHARTS CONTENT '''
    chart_semana_dash = [
                dcc.Graph(figure=chart_qnt_semana,
                animate=True, config=config_plots),
    ]

    ''' SIXTH CHARTS CONTENT '''
    chart_hora_dash = [
                dcc.Graph(figure=chart_qnt_hora,
                animate=True, config=config_plots),
    ]


    ''' ROWS CONTENT '''
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
                    dbc.Col(dbc.Card(chart_leadtime_setores_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_leadtime_unidades_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_estados_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    
                ],
            ),
        ]
    )


    row_3 = html.Div(
        [
            dbc.Row(
                [
                    #dbc.Col(dbc.Card(chart_estados_dash, className='shadow cards-info'), className='mb-4 col-lg-4 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_semana_dash, className='shadow cards-info'), className='mb-4 col-lg-6 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_hora_dash, className='shadow cards-info'), className='mb-4 col-lg-6 col-md-12 col-sm-12 col-xs-12 col-12'),
                ],
            ),
        ]
    )



    ''' END CHART CARDS' CONTENT '''
    ##############################

    ''' final layout render '''
    layout = html.Div([html.Div([row_1, row_2, row_3])])

    return layout