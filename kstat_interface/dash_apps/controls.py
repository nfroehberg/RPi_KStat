# GUI Frontend for the KStat electrochemical analyzer
# Control components for purging, stirring and progress bars
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
    print(switch, update, update_acknowledged)
    if update == update_acknowledged:
        write_config([{'component':'purge_switch','attribute':'on','value':switch}])
        root.flush()
        raise PreventUpdate
    else:
        return update
  
def stirr_switch():
    return html.Div(id='stirr_switch_container',
        className='centered_row',
        children=[
            html.Label(
                htmlFor='stirr_switch',
                children='Stirr',
                style={'width':'90px','textAlign':'right'}),
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
        raise PreventUpdate
    else:
        return update

def stirr_speed_slider():
    return html.Div(id='stirr_speed_slider_container',
        style={'width':'50%','display':'flex','flexWrap':'wrap'},
        children=[
            html.Div(style={'width':'100%','height':'30px'}),
            html.Div(
                style={'width':'100%','height':'40px'},
                children=dcc.Slider(
                id='stirr_speed_slider',
                min=200,
                max=2500,
                step=100,
                tooltip={'always_visible':True,'placement':'top'}
                )),
            html.Label(
                htmlFor='stirr_speed_slider',
                children='Stirrspeed [rpm]',
                style={'width':'100%','textAlign':'center'}),
            dcc.Store(id='stirr_speed_slider_value_update', data=1),
            dcc.Store(id='stirr_speed_slider_value_update_acknowledged', data=2)
        ])
    
@app.callback(
    Output('stirr_speed_slider_value_update_acknowledged','data'),
    [Input('stirr_speed_slider','value')],
    [State('stirr_speed_slider_value_update','data'),
     State('stirr_speed_slider_value_update_acknowledged','data')])
def update_stirr_speed(speed, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_speed_slider',
                       'attribute':'value','value':speed}])
        raise PreventUpdate
    else:
        return update

def scan_progress():
    return html.Div(id='scan_progress_container',
        style={'width':'100%'},
        children=[
            html.Div(style={'height':'5px'}),
            dbc.Progress(id='scan_progress',
                color="info",
                style={'width':'100%','height':'10px'}),
            html.Div(style={'height':'5px'}),
                ]
        )
def series_progress():
    return html.Div(id='series_progress_container',
        style={'width':'100%'},
        children=[
            html.Div(style={'height':'5px'}),
            dbc.Progress(id='series_progress',
                style={'width':'100%','height':'10px'}),
            html.Div(style={'height':'5px'}),
                ]
        )
