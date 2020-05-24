# GUI Frontend for the KStat electrochemical analyzer
# Collapsable Block to display scan parameters for voltammetric measurements underneath plot
# using Dash by Plotly (MIT licensed)
# Nico Fröhberg, 2020
# nico.froehberg@gmx.de

from time import time
from datetime import datetime
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import no_update
from redisworks import Root
from .. import redis_config
from .app import app, write_config

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

light_theme={
    'dark': False,
    'detail': '#007439',
    'primary': '#8be3ff',
    'secondary': '#6E6E6E',
}

def scan_parameters():
    return html.Div(id='scan_parameters',
        children=[
            html.Div(className='left_row',
                children=[
                    html.Button(children='Scan Parameters',
                        id='scan_parameters_button',
                        style={'width':'250px','fontSize':'xx-small','border': '1px solid #bbb','lineHeight': '20px'}),
                    html.Div(style={'width':'5px'}),
                    html.Button(children='Noise Filter Off',
                        id='noise_filter_button',
                        style={'width':'120px','fontSize':'xx-small','border': '1px solid #bbb','lineHeight': '20px','padding':'0 0'}),
                    html.Div(style={'width':'5px'}),
                    dcc.Input(id='noise_frequency_input',
                        type='number',
                        style={'backgroundColor':'transparent','color':'rgb(200, 200, 200)','width':'50px','height':'20px',
                        'fontSize':'small','textAlign':'center','border': '1px solid #bbb'},
                        debounce=True,
                        value=50,
                        ),
                    html.Label(htmlFor='noise_frequency_input',
                        children='Hz AC',
                        style={'width':'70px','height':'20px','fontSize':'small','padding':'5px 5px'}),]),
            dbc.Collapse(id='scan_parameters_collapse',
                children='Hello')])
   
@app.callback(
    Output('scan_parameters_collapse','is_open'),
    [Input('scan_parameters_button','n_clicks')],
    [State('scan_parameters_collapse','is_open')])
def open_scan_parameters(n_clicks,is_open):
    if n_clicks != None:
        if is_open:
            return False
        else:
            return True
    else:
        raise PreventUpdate