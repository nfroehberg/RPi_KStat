# GUI Frontend for the KStat electrochemical analyzer
# This script provides status indicating components like LED indicators
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

def status_indicator_leds():
    return html.Div(
        className='sub_program',
        children=[
            html.Div(
                className='centered_row',
                children=html.H5('Status')
                ),
            html.Div(
                className='centered_row',
                children=[
                    html.Label(htmlFor='electrode_test_purge_indicator',children='Purge'),
                    html.Div(style={'width':'5px'}),
                    daq.Indicator(id="electrode_test_purge_indicator",size=20),
                    
                    html.Div(style={'width':'15px'}),
                    
                    html.Label(htmlFor='electrode_test_stirr_indicator',children='Stirring'),
                    html.Div(style={'width':'5px'}),
                    daq.Indicator(id="electrode_test_stirr_indicator",size=20),
                    
                    html.Div(style={'width':'15px'}),
                    
                    html.Label(htmlFor='electrode_test_scan_indicator',children='Scan'),
                    html.Div(style={'width':'5px'}),
                    daq.Indicator(id='electrode_test_scan_indicator',size=20)
                    ]
                )
            ]
        )