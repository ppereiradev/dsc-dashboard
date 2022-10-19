from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from ..app import config_plots

def charts(conectividade):
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
    df_satisfacao = conectividade.satisfaction_customers
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
                                annotation_text= "<sup>Fechados: " + str(conectividade.closed_tickets_total) + " | </sup>"
                                                 + "<sup>Respostas: " + str(df_satisfacao['qnt'].sum()) + "</sup><br>"
                                                 + "<sup>Percentual: " + f"{(df_satisfacao['qnt'].sum()/conectividade.closed_tickets_total)*100:.2f}%" + "</sup><br>"+ f"Média: {media_satisfacao:.2f}",
                                annotation_position="top",
                                annotation_font_color="#f17e5d",
                                annotation_font_size=20)

    
    # CHAMADOS POR ESTADO
    df_completo_estados = conectividade.num_tickets_by_state
    
    chart_estados = go.Figure()
    chart_estados.add_trace(go.Bar(
        x=df_completo_estados.index,
        y=df_completo_estados['abertos'],
        name='Abertos',
        marker_color='#FF6353',
    ))

    chart_estados.add_trace(go.Bar(
        x=df_completo_estados.index,
        y=df_completo_estados['fechados'],
        name='Fechados',
        marker_color='lightsalmon',
    ))

    chart_estados.add_trace(go.Bar(
        x=df_completo_estados.index,
        y=df_completo_estados['acumulados'],
        name='Acumulados',
        marker_color='#FEBD11',
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


    df_leadtime_bar = conectividade.leadtime_bar_plot
    chart_leadtime_bar = go.Figure()
    
    chart_leadtime_bar.add_trace(go.Bar(
        x=df_leadtime_bar['mes/ano'],
        y=df_leadtime_bar["diff"],
        marker_color='#FF6353',
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


    df_leadtime_scatter = conectividade.leadtime_scatter_plot
    chart_leadtime_scatter = px.scatter(df_leadtime_scatter, x='close_at', y='diff', color="mes/ano", labels={'mes/ano':"Mes/Ano"}, 
                                        hover_data={'close_at':False,
                                                    'diff':False,
                                                    'Número':df_leadtime_scatter['number'],
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

    chart_leadtime_scatter.update_traces(marker_size=4)
    chart_leadtime_scatter.update_xaxes(tickformat="%d/%m/%Y")


    chart_leadtime_box = px.box(df_leadtime_scatter, x="mes/ano", y="diff",
                                hover_data={'close_at':False,
                                            'diff':False,
                                            'Número':df_leadtime_scatter['number'],
                                            'Aberto':df_leadtime_scatter['created_at'].dt.strftime('%d/%m/%y'),
                                            'Fechado':df_leadtime_scatter['close_at'].dt.strftime('%d/%m/%y'),
                                            'Dias':df_leadtime_scatter['diff'],
                            })
    chart_leadtime_box.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    chart_leadtime_box.update_layout(
        title="Leadtime (dias)",
        xaxis_title="Data",
        yaxis_title='Dias',
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=350,
        margin=dict(l=0, r=10, t=100, b=0),
    )

    chart_leadtime_box.update_traces(marker_size=4)


    # table
    headerColor = 'grey'
    rowEvenColor = 'rgba(0,0,0,0.05)'
    rowOddColor = 'white'

    chart_table_tickets_gt_20 = go.Figure(data=[go.Table(
                                                    columnwidth = [40, 500, 100, 70],
                                                    header=dict(
                                                        values=['#', 'Título', 'Data de Abertura', 'Dias Aberto'],
                                                        line_color='darkslategray',
                                                        fill_color=headerColor,
                                                        align=['left','center'],
                                                        font=dict(color='white', size=16)
                                                    ),
                                                    cells=dict(values=[conectividade.tickets_opened_more_20_days['id_ticket'],
                                                        conectividade.tickets_opened_more_20_days['title'],
                                                        conectividade.tickets_opened_more_20_days['created_at'].dt.strftime('%d/%m/%Y'),
                                                        conectividade.tickets_opened_more_20_days['idade'] 
                                                    ],
                                                    line_color='darkslategray',
                                                    # 2-D list of colors for alternating rows
                                                    fill_color = [[rowOddColor,rowEvenColor]
                                                                    *(len(conectividade.tickets_opened_more_20_days['id_ticket'])-2 
                                                                    if len(conectividade.tickets_opened_more_20_days['id_ticket']) > 2
                                                                    else 1)],
                                                    align = ['left', 'left', 'center'],
                                                    font = dict(color = 'darkslategray', size = 14)
                                                    
                                                    ))
                                                ])

    chart_table_tickets_gt_20.update_layout(
        title="Número de Chamados Abertos há Mais de 20 dias<br><sup></sup>"
              + "<sup>Número Total: " + str(conectividade.tickets_opened_more_20_days.count()[0]) + "</sup>",
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#252422', "family":"Montserrat"},
        height=500,
        margin=dict(l=50, r=10, t=100, b=40),
    )


    return {"satisfacao": chart_satisfacao,
            "estados": chart_estados,
            "leadtime-bar": chart_leadtime_bar,
            "leadtime-scatter": chart_leadtime_scatter,
            "leadtime-box": chart_leadtime_box,
            "table-tickets-gt-20": chart_table_tickets_gt_20,
            }


def app_content(charts, conectividade):
    """
    Build the html components.

    Use html components with ``charts`` parameters
    to build the layout of the dashboard.

    Parameters
    ----------
    charts : dict of {str : plotly.graph_objects and plotly.express}
        Dictionary that contains the charts.
    data : dict of {str : int or pd.DataFrame}
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
                html.Div(html.P(conectividade.open_tickets_current_month,className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    card_fechados_corrente = [
        dbc.CardHeader("Fechados", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="fas fa-check-double fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(conectividade.closed_tickets_current_month,className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    card_acumulados_corrente = [
        dbc.CardHeader("Acumulados", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="fas fa-archive fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(conectividade.num_accumulated_tickets,className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]


    # FIRST CHARTS CONTENT
    chart_satisfacao_dash = [
        
                dcc.Graph(figure=charts["satisfacao"],
                animate=False, config=config_plots),
    ]

    # SECOND CHARTS CONTENT
    chart_estados_dash = [
        
                dcc.Graph(figure=charts["estados"],
                animate=False, config=config_plots),
    ]

    # THREE CHARTS CONTENT
    chart_leadtime_bar_dash = [
        
                dcc.Graph(figure=charts["leadtime-bar"],
                animate=False, config=config_plots),
    ]

    # FOURTH CHARTS CONTENT
    chart_leadtime_scatter_dash = [
        
                dcc.Graph(figure=charts["leadtime-scatter"],
                animate=False, config=config_plots),
    ]

    # FIFTH CHARTS CONTENT
    chart_leadtime_box_dash = [
        
                dcc.Graph(figure=charts["leadtime-box"],
                animate=False, config=config_plots),
    ]


    chart_table_tickets_gt_20 = [
                dcc.Graph(figure=charts["table-tickets-gt-20"],
                animate=False, config=config_plots),
        
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
                    dbc.Col(dbc.Card(chart_leadtime_scatter_dash, className='shadow cards-info'), className='mb-4 col-lg-6 col-md-12 col-sm-12 col-xs-12 col-12'),
                    dbc.Col(dbc.Card(chart_leadtime_box_dash, className='shadow cards-info'), className='mb-4 col-lg-6 col-md-12 col-sm-12 col-xs-12 col-12'),
                ],
            ),
        ]
    )

    if len(conectividade.tickets_opened_more_20_days['title']) > 0:
        row_4 = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(chart_table_tickets_gt_20, className='shadow cards-info'), className='mb-4 col-lg-12 col-md-12 col-sm-12 col-xs-12 col-12'),
                    ], className='justify-content-center',
                ),
            ]
        )

        return html.Div([html.Div([row_1, row_2, row_3, row_4])])
    
    else:
        return html.Div([html.Div([row_1, row_2, row_3])])


def layout(conectividade):
    """
    Build the html layout of the third tab.

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
    return app_content(charts(conectividade), conectividade)
