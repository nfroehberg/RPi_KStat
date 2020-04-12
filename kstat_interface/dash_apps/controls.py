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

light_theme={
    'dark': False,
    'detail': '#007439',
    'primary': '#8be3ff',
    'secondary': '#6E6E6E',
}

def purge_switch():
    return html.Div(id='purge_switch_container',
        className='centered_row',
        children=[
            daq.BooleanSwitch(id="purge_switch",style={'width':'90px'}),
            html.Label(
                htmlFor='purge_switch',
                children='Purge',
                style={'width':'90px'}),
            dcc.Store(id='purge_switch_on_update', data=1),
            dcc.Store(id='purge_switch_on_update_acknowledged', data=2),]
    )
    
# if state of purge switch changes, write to config file
@app.callback(
    Output('purge_switch_on_update_acknowledged','data'),
    [Input('purge_switch','on')],
    [State('purge_switch_on_update','data'),
    State('purge_switch_on_update_acknowledged','data')])
def control_purging(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'purge_switch','attribute':'on','value':switch}])
        root.flush()
        raise PreventUpdate
    else:
        return update
        
def stirr_switch():
    return html.Div(id='stirr_switch_container',
        style={'display':'none'},
        className='centered_row',
        children=[
            html.Label(
                htmlFor='stirr_switch',
                children='Stirr',
                style={'width':'90px'}),
            daq.BooleanSwitch(id="stirr_switch",style={'width':'90px'}),
            dcc.Store(id='stirr_switch_on_update', data=1),
            dcc.Store(id='stirr_switch_on_update_acknowledged', data=2),]
    )

     
# if state of stirr switch changes, write to config file
@app.callback(
    Output('stirr_switch_on_update_acknowledged','data'),
    [Input('stirr_switch','on')],
    [State('stirr_switch_on_update','data'),
    State('stirr_switch_on_update_acknowledged','data')])
def control_stirring(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_switch','attribute':'on','value':switch}])
        root.flush()
        raise PreventUpdate
    else:
        return update