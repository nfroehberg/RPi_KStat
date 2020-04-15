# GUI Frontend for the KStat electrochemical analyzer
# This script provides plotly graphs of voltammetric scans
# using Dash by Plotly (MIT licensed)
# Nico Fröhberg, 2019
# nico.froehberg@gmx.de

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import no_update
from time import time,sleep
from redisworks import Root
from ast import literal_eval
import json
from .app import app, write_config
from .. import redis_config
import pandas as pd

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

def plot_scan():
    return html.Div(id='voltammogram_graph_container',
        style={'width':'100%'},
        children=[
            dcc.Store(id='voltammogram_graph_file'),
            dcc.Graph(id='voltammogram_graph'),
            ]
        )

@app.callback(
    Output('voltammogram_graph','figure'),
    [Input('voltammogram_graph_file','data')])
def update_plot_scan(file):
    df=pd.read_csv(file)
    root.flush()
    config = literal_eval(str(root.electrode_test))
    graph_title = file.replace(str(root.working_directory),'').replace('.csv','')
    figure={
        'data':[{'x':df.potential,
                 'y':df.current,
                 'marker':{'color':'rgb(155,240,255)'}
                 }
                ],
        'layout':{
            'title':{
                'text':graph_title,
                'font':{'color':'white'}},
            'xaxis':{
                'title':{
                    'text':'Potential [mV] vs. Ag/AgCl',
                    'font':{'color':'white'}},
                'autorange':'reversed',
                'gridcolor':'black',
                'zerolinecolor':'black',
                'zerolinewidth':2,
                'tickfont':{'color':'white'}
                },
            'yaxis':{
                'title':{
                    'text':'Current [A]',
                    'font':{'color':'white'}},
                'autorange':'reversed',
                'gridcolor':'black',
                'zerolinecolor':'black',
                'zerolinewidth':2,
                'tickfont':{'color':'white'}
                },
            'paper_bgcolor':'rgba(0,0,0,0)',
            'plot_bgcolor':'rgba(0,0,0,0)'
            }
        }
    return figure