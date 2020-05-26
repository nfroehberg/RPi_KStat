# GUI Frontend for the KStat electrochemical analyzer
# Script to provide update component that checks for changes from the backend 
# to update the interface output
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
from glob import glob

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

# (<component>,<parameter>,<user updatable>)
update_list=[
    ('purge_switch','on',True),
    ('purge_switch','disabled',False),
    ('stirr_switch','on',True),
    ('stirr_switch','disabled',False),
    ('scan_progress','value',False),
    ('scan_progress_label','children',False),
    ('series_progress','value',False),
    ('series_progress_label','children',False),
    ('stirr_speed_slider','value',True),
    ('cleaning_potential_input','value',True),
    ('deposition_potential_input','value',True),
    ('cleaning_time_input','value',True),
    ('deposition_time_input','value',True),
    ('purge_time_input','value',True),
    ('start_potential_input','value',True),
    ('end_potential_input','value',True),
    ('vertex_potential_input','value',True),
    ('slope_input','value',True),
    ('pulse_height_input','value',True),
    ('samplefreq_input','value',True),
    ('iv_gain_input','value',True),
    ('pga_gain_input','value',True),
    ('n_scans_input','value',True),
    ('step_size_input','value',True),
    ('period_input','value',True),
    ('pulse_width_input','value',True),
    ('frequency_input','value',True),
    ('category_selection','value',True),
    ('program_selection','value',True),
    ('program_selection','options',False),
    ('plating_time_input','value',True),
    ('plating_potential_input','value',True),
    ('comment_input','value',True),
    ('n_electrode_tests_input','value',True),
    ('start_button','disabled',False),
    ('stop_button','disabled',False),
    ('graph_file','data',False),
    ('change_directory_button','disabled',False),
    ('upload_button','disabled',False),
    ('download_button','disabled',False),
    ('noise_filter_button','children',False),
    ('noise_frequency_input','value',True),
    ]

####################################################################
def update_components():
    return html.Div(
        children=[
            dcc.Interval(
                id='update_interval',
                interval=100, # in milliseconds
                n_intervals=0
            ),
            dcc.Store(id='update_timestamp', data=1)
            ])
        
        
####################################################################
# Getting Changes from Backend
####################################################################

# check if timestamp of redis server changed to trigger config update
@app.callback(
    Output('update_timestamp','data'),
    [Input('update_interval','n_intervals')],
    [State('update_timestamp','data')])
def check_update(n_intervals, stored_stamp):
    # get time stamp of config in redis server
    try:
        root.flush()
        config_stamp = str(root['update_timestamp'])
    except Exception as e:
        print("Couldn't load config time stamp.", e)
        raise PreventUpdate
    # if stored time stamp matches config, no update is necessary
    # otherwise get config from redis server
    if config_stamp == str(stored_stamp):
        raise PreventUpdate
    else:
        return config_stamp



# generating lists of parameters for callback function
update_outputs = []
update_states = []
factors = []
user_updatable = []
for parameter in update_list:
    update_outputs.append(Output(parameter[0], parameter[1]))
    update_states.append(State(parameter[0], parameter[1]))
    factors.append(parameter[0] + '.' + parameter[1])
    user_updatable.append(parameter[2])
    if parameter[2]:
        update_outputs.append(Output(parameter[0]+'_'+parameter[1]+'_update', 'data'))
        update_states.append(State(parameter[0]+'_'+parameter[1]+'_update', 'data'))
        factors.append(parameter[0] +'_'+parameter[1]+ '_update.data')
        user_updatable.append(parameter[2])
factor_labels=factors


@app.callback(
    update_outputs,
    [Input('update_timestamp','data')],
    update_states)
def update_config(timestamp,*factors):
    try:
        root.flush()
        config = literal_eval(str(root.config))
    except Exception as e:   
        print("Couldn't load config.", e)
        raise PreventUpdate
        
    factors = list(factors)
    output_factors = []
    for i in range(len(factors)):
        if 'update' in factor_labels[i]:
            pass
        else:
            component = factor_labels[i][:factor_labels[i].find('.')]
            parameter = factor_labels[i][factor_labels[i].find('.')+1:]
            config_value = config[component][parameter]
            component_value = factors[i]
            if config_value != component_value:
                output_factors.append(config_value)
                if user_updatable[i]:
                    output_factors.append(factors[i+1]+1)
            else:
                output_factors.append(no_update)
                if user_updatable[i]:
                    output_factors.append(no_update)
    return tuple(output_factors)
