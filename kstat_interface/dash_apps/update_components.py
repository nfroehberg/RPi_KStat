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

def update_components():
    return html.Div(
        children=[
            dcc.Interval(
                id='update_interval',
                interval=250, # in milliseconds
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

# (<component>,<parameter>,<user updatable>)
update_list=[
    ('purge_switch','on',True),
    ('purge_switch','disabled',False),
    ('stirr_switch','on',True),
    ('stirr_switch','disabled',False),
    ]

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
