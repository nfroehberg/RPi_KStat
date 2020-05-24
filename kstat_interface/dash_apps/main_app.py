# GUI Frontend for the KStat electrochemical analyzer
# main application structure for graph, controls and inputs
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
from .app import app, write_config
from .. import redis_config
from .update_components import update_components
from .file_management import directory_and_scan_selection
from .controls import *
from .inputs import *
from .program_selection import *
from .stopandgo import *
from .plotting import plot_scan
from .scan_parameters import scan_parameters
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
        html.Div(id='graph_and_file_management',
            className='sub_program',
            style={'width':'100%','display':'flex','flexWrap':'wrap'},
            children=[
                plot_scan(),
                scan_parameters(),
                directory_and_scan_selection()
                ]
            ),
                
        html.Div(id='controls',
            className='sub_program',
            style={'width':'100%'},
            children=[
                html.H5('Controls'),
                html.Div(
                    className='centered_row',
                    children=[
                        start(),
                        stop(),
                        ]
                    ),
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
                html.H5('Settings'),
                html.Div(
                    className='centered_row',
                    children=[
                        category_selection(),
                        program_selection()]),
                html.Div(
                    className='left_row',
                    children=[
                        purge_time(),
                        cleaning_potential(),
                        cleaning_time(),
                        deposition_potential(),
                        deposition_time(),
                        start_potential(),
                        vertex_potential(),
                        end_potential(),
                        slope(),
                        pulse_height(),
                        pulse_width(),
                        period(),
                        frequency(),
                        step_size(),
                        n_scans(),
                        samplefreq(),
                        iv_gain(),
                        pga_gain(),
                        plating_time(),
                        plating_potential(),
                        comment(),
                        n_electrode_tests(),
                        ]
                    )
            ]
        )
    ])

