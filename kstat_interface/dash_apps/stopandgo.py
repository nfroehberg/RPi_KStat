# GUI Frontend for the KStat electrochemical analyzer
# start and stop buttons for all programs and the associated confirmation popups
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

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)


def start():
    return html.Div(id='start_button_container',
        style={'width':'40%'},
        children=[
            html.Button(id='start_button',
                children='Start',
                style={'width':'90%'})
            ]
        )
        
def stop():
    return html.Div(id='stop_button_container',
        style={'width':'40%'},
        children=[
            html.Button(id='stop_button',
                children='Stop',
                style={'width':'90%'})
            ]
        )