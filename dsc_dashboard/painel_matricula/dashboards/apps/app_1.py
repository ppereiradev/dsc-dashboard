from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

import plotly.express as px

from ..app import config_plots

def layout(matriculas):
    fig_matriculas = px.line(matriculas, x='data', y='quantidade', markers=True)
    
    card_matriculas = [
        dbc.CardHeader("Total de Solicitações de Matricula", className='cards-content-info-header'),
        dbc.CardBody(
            [
                html.Div(html.I(className="far fa-clipboard fa-2x"), className='div-icon-card-body'),
                html.Div(html.P(matriculas['quantidade'].sum(),className="card-text cards-content-info-body"), className='div-content-card-body'),
            ],
            className="cards-info-body"),
    ]

    chart_matriculas = [
        dcc.Graph(figure=fig_matriculas,
        animate=False, config=config_plots),
    ]

    row_1 = html.Div(
        [   
            dbc.Row(
                [
                    dbc.Col(dbc.Card(card_matriculas, className='shadow cards-info'), className='mb-4 col-lg-6 col-md-6 col-sm-12 col-xs-12 col-12'),
                ]
            )
        ], className='justify-content-lg-center'
    )

    row_2 = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(chart_matriculas, className='shadow cards-info'), className='mb-4 col-lg-12 col-md-12 col-sm-12 col-xs-12 col-12'),
                ],
            ),
        ], className='justify-content-md-center'
    )
    
    return html.Div([row_1, row_2])
