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
from .app import app, write_config
from .. import redis_config
from .update_components import update_components
from .controls import *
from .inputs import *
from .plotting import plot_scan
import pandas as pd
from glob import glob

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

light_theme={
    'dark': False,
    'detail': '#007439',
    'primary': '#8be3ff',
    'secondary': '#6E6E6E',
}

def main():
    return html.Div(
        className='main_program',
        children=[
        update_components(),
        
        #plot_scan(),
                
        html.Div(id='controls',
            className='sub_program',
            style={'width':'100%'},
            children=[
                html.H5('Controls'),
                html.Div(
                    className='centered_row',
                    children=[
                        purge_switch(),
                        stirr_speed_slider(),
                        stirr_switch(),
                        ]
                    ),
                html.Div(
                    className='centered_row',
                    children=[
                        scan_progress(),
                        series_progress(),
                        ]
                    ),
                ]
            ),
            
        html.Div(id='scan_settings',
            className='sub_program',
            children=[
                html.H5('Scan Settings'),
                html.Div(
                className='centered_row',
                children=[]
                )
            ]
        )
    ])

