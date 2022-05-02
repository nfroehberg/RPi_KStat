# GUI Frontend for the KStat electrochemical analyzer
# main application structure for graph, controls and inputs
# using Dash by Plotly (MIT licensed)
# Nico Fröhberg, 2019
# nico.froehberg@gmx.de

import dash
from dash import dcc
from dash import html
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions import EventListener
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
        EventListener(id='keyboard'),
        html.Div(id="output"),
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
                html.Div(style={'height':'10px','width':'100%'}),
                html.Div(
                    className='centered_row',
                    children=[
                        purge_switch(),
                        stirr_speed_slider(),
                        stirr_switch(),
                        ]
                    ),
                html.Div(style={'height':'10px','width':'100%'}),
                html.Div(
                    className='centered_row',
                    children=[
                        home_button(),
                        move_step_button(),
                        ]
                    ),
                html.Div(style={'height':'10px','width':'100%'}),
                html.Div(
                    className='centered_row',
                    children=[
                        scan_progress(),
                        series_progress(),
                        ]
                    ),
                html.Div(style={'height':'10px','width':'100%'}),
                html.Div(
                    className='centered_row',
                    children=[
                        profiler_position()
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
                        html.Div(style={'width':'5%'}),
                        program_selection(),
                        html.Div(style={'width':'5%'}),
                        config_selection()]),
                html.Div(
                    className='left_row',
                    children=[
                        profile_step_distance(),
                        profile_step_number(),
                        profile_repeat_measurements(),
                        max_speed(),
                        max_acceleration(),
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
    
# capture keystrokes and use for hotkey functions
@app.callback([Output('next_scan_key','data'),
               Output('previous_scan_key','data')], 
             [Input("keyboard", "n_events")],
             [State('keyboard','event')])
def keydown(n_keydown,event):
    if event is None:
        raise PreventUpdate()
    print('Key pressed', event)
    if event['key'] == 'x':
        return [time(),no_update]
    elif event['key'] == 'y':
        return [no_update,time()]
    else:
        raise PreventUpdate
