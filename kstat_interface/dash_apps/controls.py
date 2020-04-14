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
        style={'width':'50%'},
        children=[
            html.Div(
                style={'width':'100%'},
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

def category_selection():
    return html.Div(id='category_selection_container',
        style={'width':'30%'},
        children=[
            dcc.Store(id='category_selection_value_update', data=1),
            dcc.Store(id='category_selection_value_update_acknowledged', data=2),
            dcc.Dropdown(
                id='category_selection',
                style={'color':'black'},
                clearable=False,
                options=[
                    {'label':'Voltammetry - Single Measurement','value':'voltammetry_single'},
                    {'label':'Voltammetry - Standard Addition','value':'voltammetry_standard_addition'},
                    {'label':'Hg/Au Electrode Fabrication','value':'hg_au_electrode_fabrication'},
                    ]
                ),
            ]
        )
@app.callback(
    [Output('category_selection_value_update_acknowledged','data'),
    Output('program_selection','options')],
    [Input('category_selection','value')],
    [State('category_selection_value_update','data'),
     State('category_selection_value_update_acknowledged','data')])
def update_category(value, update, update_acknowledged):
    if update == update_acknowledged:
        
        write_config([{'component':'category_selection',
                       'attribute':'value','value':value}])
                       
        if value == 'voltammetry_single':
            options = [
                {'label':'Cyclic','value':'single_cv'},
                {'label':'Linear','value':'single_lv'},
                {'label':'Differential Pulse','value':'single_dpv'},
                {'label':'Squarewave','value':'single_swv'},]
        elif value == 'voltammetry_standard_addition':
            options = [
                {'label':'Cyclic','value':'standard_addition_cv'},
                {'label':'Linear','value':'standard_addition_lv'},
                {'label':'Differential Pulse','value':'standard_addition_dpv'},
                {'label':'Squarewave','value':'standard_addition_swv'},]
        elif value == 'hg_au_electrode_fabrication':
            options = [
                {'label':'Mercury Plating','value':'hg_au_electrode_plating'},
                {'label':'Electrode Testing','value':'hg_au_electrode_testing'}]
        else:
            options = []
            
        return no_update, options
    else:
        return update, no_update

def program_selection():
    return html.Div(id='program_selection_container',
        style={'width':'30%'},
        children=[
            dcc.Store(id='program_selection_value_update', data=1),
            dcc.Store(id='program_selection_value_update_acknowledged', data=2),
            dcc.Dropdown(
                id='program_selection',
                style={'color':'black'},
                clearable=False,
                ),
            ]
        )
@app.callback(
    Output('program_selection_value_update_acknowledged','data'),
    [Input('program_selection','value')],
    [State('program_selection_value_update','data'),
     State('program_selection_value_update_acknowledged','data')])
def update_program(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'program_selection',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update