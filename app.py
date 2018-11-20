import dash
import dash_html_components as html
import dash_core_components as dcc
import requests
import json
import plotly.plotly as py
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State, Event
import datetime
from collections import defaultdict
import pandas as pd

import flask

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

times = list()
symbols = ['USD', 'BRL', 'CAD', 'EUR']
hists = defaultdict(list)

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets
)

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

server = app.server
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2('Dash Bitcoin',
                    style={'display': 'inline',
                           'float': 'left',
                           'font-size': '2.65em',
                           'margin-left': '7px',
                           'font-weight': 'bolder',
                           'font-family': 'Product Sans',
                           'color': "rgba(117, 117, 117, 0.95)",
                           'margin-top': '20px',
                           'margin-bottom': '0'
                           }),
            html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                     style={
                         'height': '100px',
                         'float': 'right'
                     }),
        ], className='row'),
        html.Div([
            dcc.Tabs(id="tabs", value='tab-1', children=[
                dcc.Tab(label='Cotação em tempo real', value='tab-1',style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Cotação mensal', value='tab-2',style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Conversão de valores', value='tab-3',style=tab_style, selected_style=tab_selected_style),
            ]),
        ], className='row')
    ]),

    html.Div(id='tabs-content')

], className="container")


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Div([
                dcc.Graph(id='quote-btc-graph'),
            ]),
            dcc.Interval(id='quote-update', interval=5000, n_intervals=0),
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Div([
                dcc.Dropdown(
                    id='symbol-select-graph',
                    options=[{'label':symbol, 'value':symbol} for symbol in symbols],
                    value=symbols[0] 
                ),
            ]),
            dcc.Graph(id='graph-monthly')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.Div([
                dcc.Input(
                    id='value-2-convert',
                    placeholder='Entre com um valor',
                    type='number',
                    value=0
                ),
                dcc.Dropdown(
                    id='symbol-select',
                    options=[{'label':symbol, 'value':symbol} for symbol in symbols],
                    value=symbols[0] 
                ),
            ], className='four columns'),
            html.Div([  
                html.H3(id='result-conversao', style={'text-align':'centers'})
            ], className='eight columns') 
        ], className='row', style={'padding-top':'2%'})


@app.callback(Output('quote-btc-graph', 'figure'), [Input('quote-update', 'n_intervals')])
def quote_btc(interval):

    trace = list()

    values = requests.get('https://blockchain.info/ticker')
    values = values.json()

    times.append(datetime.datetime.now())
    for symbol in symbols:
        hists[symbol].append(values[symbol]['last'])
        trace.append(
            {'x': times, 'y': hists[symbol], 'type': 'scatter', 'name': symbol})

    layout = Layout(
        title="Cotação do Bitcoin em tempo real",
        height=500,
        xaxis=dict(
            title='Tempo'
        ),
        yaxis=dict(
            title='Cotação'
        ),
    )

    return Figure(data=trace, layout=layout)

@app.callback(
    dash.dependencies.Output('result-conversao', 'children'),
    [dash.dependencies.Input('value-2-convert', 'value'),
    dash.dependencies.Input('symbol-select', 'value')])
def update_conversao(value2convert ,value):
    result_conversao = requests.get('https://blockchain.info/tobtc?currency='+ value + '&value='+str(value2convert) )
    result_conversao = result_conversao.json()

    return "{} {} -> {} BTC".format(value2convert,value, result_conversao)

@app.callback(dash.dependencies.Output('graph-monthly', 'figure'),[dash.dependencies.Input('symbol-select-graph', 'value')])
def update_conversao(symbol):

    values = requests.get('https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=BTC&market='+ symbol +'&apikey=QMZNNXTL7TSKW6KX')
    values = values.json()
    values = values['Time Series (Digital Currency Monthly)']

    candlestick = {
        'x': [value for value in values],
        'open': [value['1a. open ('+ symbol +')'] for value in values.values()],
        'high':  [value['2a. high ('+ symbol +')'] for value in values.values()],
        'low':  [value['3a. low ('+ symbol +')'] for value in values.values()],
        'close':  [value['4a. close ('+ symbol +')'] for value in values.values()],
        'type': 'candlestick',
        'name': symbol,
        'legendgroup': symbol
    }

    layout = {'title': 'Histórico do bitcoin para ' + symbol}

    return Figure(data=[candlestick], layout=layout)

if __name__ == '__main__':
    app.run_server(debug=True)
