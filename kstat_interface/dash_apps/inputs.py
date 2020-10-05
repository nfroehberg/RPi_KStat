# GUI Frontend for the KStat electrochemical analyzer
# Input components to set measurement parameters
# using Dash by Plotly (MIT licensed)
# Nico Fröhberg, 2019
# nico.froehberg@gmx.de
# requires backend script (KStat_Dash_Back.py)
# for control of the KStat as well as purging and stirring

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

def max_acceleration():
    return html.Div(id='max_acceleration_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='max_acceleration_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='max_acceleration_input_value_update', data=1),
            dcc.Store(id='max_acceleration_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='max_acceleration_input',
                       children=['Max',html.Br(),'Acceleration [mm/s²]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('max_acceleration_input_value_update_acknowledged','data'),
    [Input('max_acceleration_input','value')],
    [State('max_acceleration_input_value_update','data'),
     State('max_acceleration_input_value_update_acknowledged','data')])
def update_max_acceleration(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'max_acceleration_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def max_speed():
    return html.Div(id='max_speed_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='max_speed_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='max_speed_input_value_update', data=1),
            dcc.Store(id='max_speed_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='max_speed_input',
                       children=['Max',html.Br(),'Speed [mm/s]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('max_speed_input_value_update_acknowledged','data'),
    [Input('max_speed_input','value')],
    [State('max_speed_input_value_update','data'),
     State('max_speed_input_value_update_acknowledged','data')])
def update_max_speed(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'max_speed_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def profile_repeat_measurements():
    return html.Div(id='profile_repeat_measurements_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='profile_repeat_measurements_input',
                        min=0,
                        max=99,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='profile_repeat_measurements_input_value_update', data=1),
            dcc.Store(id='profile_repeat_measurements_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='profile_repeat_measurements_input',
                       children=['Measurement',html.Br(),'Replicates'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('profile_repeat_measurements_input_value_update_acknowledged','data'),
    [Input('profile_repeat_measurements_input','value')],
    [State('profile_repeat_measurements_input_value_update','data'),
     State('profile_repeat_measurements_input_value_update_acknowledged','data')])
def update_profile_repeat_measurements(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'profile_repeat_measurements_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def profile_step_number():
    return html.Div(id='profile_step_number_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='profile_step_number_input',
                        min=0,
                        max=999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='profile_step_number_input_value_update', data=1),
            dcc.Store(id='profile_step_number_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='profile_step_number_input',
                       children=['Profile',html.Br(),'Step Number'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('profile_step_number_input_value_update_acknowledged','data'),
    [Input('profile_step_number_input','value')],
    [State('profile_step_number_input_value_update','data'),
     State('profile_step_number_input_value_update_acknowledged','data')])
def update_profile_step_number(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'profile_step_number_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def profile_step_distance():
    return html.Div(id='profile_step_distance_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='profile_step_distance_input',
                        min=-500,
                        max=500,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='profile_step_distance_input_value_update', data=1),
            dcc.Store(id='profile_step_distance_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='profile_step_distance_input',
                       children=['Profile',html.Br(),'Step [mm]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('profile_step_distance_input_value_update_acknowledged','data'),
    [Input('profile_step_distance_input','value')],
    [State('profile_step_distance_input_value_update','data'),
     State('profile_step_distance_input_value_update_acknowledged','data')])
def update_profile_step_distance(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'profile_step_distance_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def cleaning_potential():
    return html.Div(id='cleaning_potential_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='cleaning_potential_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='cleaning_potential_input_value_update', data=1),
            dcc.Store(id='cleaning_potential_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='cleaning_potential_input',
                       children=['Cleaning',html.Br(),'Potential [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('cleaning_potential_input_value_update_acknowledged','data'),
    [Input('cleaning_potential_input','value')],
    [State('cleaning_potential_input_value_update','data'),
     State('cleaning_potential_input_value_update_acknowledged','data')])
def update_cleaning_potential(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'cleaning_potential_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def deposition_potential():
    return html.Div(id='deposition_potential_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='deposition_potential_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='deposition_potential_input_value_update', data=1),
            dcc.Store(id='deposition_potential_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='deposition_potential_input',
                       children=['Deposition',html.Br(),'Potential [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('deposition_potential_input_value_update_acknowledged','data'),
    [Input('deposition_potential_input','value')],
    [State('deposition_potential_input_value_update','data'),
     State('deposition_potential_input_value_update_acknowledged','data')])
def update_deposition_potential(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'deposition_potential_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def cleaning_time():
    return html.Div(id='cleaning_time_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='cleaning_time_input',
                        min=0,
                        max=1200,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='cleaning_time_input_value_update', data=1),
            dcc.Store(id='cleaning_time_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='cleaning_time_input',
                       children=['Cleaning',html.Br(),'Time [s]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('cleaning_time_input_value_update_acknowledged','data'),
    [Input('cleaning_time_input','value')],
    [State('cleaning_time_input_value_update','data'),
     State('cleaning_time_input_value_update_acknowledged','data')])
def update_cleaning_time(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'cleaning_time_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def deposition_time():
    return html.Div(id='deposition_time_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='deposition_time_input',
                        min=0,
                        max=1200,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='deposition_time_input_value_update', data=1),
            dcc.Store(id='deposition_time_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='deposition_time_input',
                       children=['Deposition',html.Br(),'Time [s]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('deposition_time_input_value_update_acknowledged','data'),
    [Input('deposition_time_input','value')],
    [State('deposition_time_input_value_update','data'),
     State('deposition_time_input_value_update_acknowledged','data')])
def update_deposition_time(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'deposition_time_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def purge_time():
    return html.Div(id='purge_time_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='purge_time_input',
                        min=0,
                        max=1200,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='purge_time_input_value_update', data=1),
            dcc.Store(id='purge_time_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='purge_time_input',
                       children=['Purge',html.Br(),'Time [s]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('purge_time_input_value_update_acknowledged','data'),
    [Input('purge_time_input','value')],
    [State('purge_time_input_value_update','data'),
     State('purge_time_input_value_update_acknowledged','data')])
def update_purge_time(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'purge_time_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def start_potential():
    return html.Div(id='start_potential_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='start_potential_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='start_potential_input_value_update', data=1),
            dcc.Store(id='start_potential_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='start_potential_input',
                       children=['Start',html.Br(),'Potential [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('start_potential_input_value_update_acknowledged','data'),
    [Input('start_potential_input','value')],
    [State('start_potential_input_value_update','data'),
     State('start_potential_input_value_update_acknowledged','data')])
def update_start_potential(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'start_potential_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def vertex_potential():
    return html.Div(id='vertex_potential_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='vertex_potential_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='vertex_potential_input_value_update', data=1),
            dcc.Store(id='vertex_potential_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='vertex_potential_input',
                       children=['Vertex',html.Br(),'Potential [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('vertex_potential_input_value_update_acknowledged','data'),
    [Input('vertex_potential_input','value')],
    [State('vertex_potential_input_value_update','data'),
     State('vertex_potential_input_value_update_acknowledged','data')])
def update_vertex_potential(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'vertex_potential_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def end_potential():
    return html.Div(id='end_potential_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='end_potential_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='end_potential_input_value_update', data=1),
            dcc.Store(id='end_potential_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='end_potential_input',
                       children=['End',html.Br(),'Potential [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('end_potential_input_value_update_acknowledged','data'),
    [Input('end_potential_input','value')],
    [State('end_potential_input_value_update','data'),
     State('end_potential_input_value_update_acknowledged','data')])
def update_end_potential(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'end_potential_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def slope():
    return html.Div(id='slope_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='slope_input',
                        min=0,
                        max=3000,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='slope_input_value_update', data=1),
            dcc.Store(id='slope_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='slope_input',
                       children=['Slope',html.Br(),'[mV/s]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('slope_input_value_update_acknowledged','data'),
    [Input('slope_input','value')],
    [State('slope_input_value_update','data'),
     State('slope_input_value_update_acknowledged','data')])
def update_slope(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'slope_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def pulse_height():
    return html.Div(id='pulse_height_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='pulse_height_input',
                        min=0,
                        max=1000,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='pulse_height_input_value_update', data=1),
            dcc.Store(id='pulse_height_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='pulse_height_input',
                       children=['Pulse',html.Br(),'Height [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('pulse_height_input_value_update_acknowledged','data'),
    [Input('pulse_height_input','value')],
    [State('pulse_height_input_value_update','data'),
     State('pulse_height_input_value_update_acknowledged','data')])
def update_pulse_height(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'pulse_height_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def step_size():
    return html.Div(id='step_size_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='step_size_input',
                        min=0,
                        max=100,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='step_size_input_value_update', data=1),
            dcc.Store(id='step_size_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='step_size_input',
                       children=['Step',html.Br(),'Size [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('step_size_input_value_update_acknowledged','data'),
    [Input('step_size_input','value')],
    [State('step_size_input_value_update','data'),
     State('step_size_input_value_update_acknowledged','data')])
def update_step_size(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'step_size_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def period():
    return html.Div(id='period_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='period_input',
                        min=0,
                        max=5000,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='period_input_value_update', data=1),
            dcc.Store(id='period_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='period_input',
                       children=['Period',html.Br(),'[ms]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('period_input_value_update_acknowledged','data'),
    [Input('period_input','value')],
    [State('period_input_value_update','data'),
     State('period_input_value_update_acknowledged','data')])
def update_period(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'period_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def pulse_width():
    return html.Div(id='pulse_width_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='pulse_width_input',
                        min=0,
                        max=1000,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='pulse_width_input_value_update', data=1),
            dcc.Store(id='pulse_width_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='pulse_width_input',
                       children=['Pulse',html.Br(),'Width [ms]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('pulse_width_input_value_update_acknowledged','data'),
    [Input('pulse_width_input','value')],
    [State('pulse_width_input_value_update','data'),
     State('pulse_width_input_value_update_acknowledged','data')])
def update_pulse_width(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'pulse_width_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def frequency():
    return html.Div(id='frequency_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='frequency_input',
                        min=0,
                        max=500,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='frequency_input_value_update', data=1),
            dcc.Store(id='frequency_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='frequency_input',
                       children=['Frequency',html.Br(),'[Hz]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('frequency_input_value_update_acknowledged','data'),
    [Input('frequency_input','value')],
    [State('frequency_input_value_update','data'),
     State('frequency_input_value_update_acknowledged','data')])
def update_frequency(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'frequency_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def samplefreq():
    return html.Div(id='samplefreq_input_container',
        className='centered_row',
        children=[
            dcc.Store(id='samplefreq_input_value_update', data=1),
            dcc.Store(id='samplefreq_input_value_update_acknowledged', data=2),
            dcc.Dropdown(
                id='samplefreq_input',
                style={'width':'65px','color':'black','fontSize':'x-small'},
                clearable=False,
                options=[
                    {'label':'2.5 Hz','value':'2.5Hz'},
                    {'label':'5 Hz','value':'5Hz'},
                    {'label':'10 Hz','value':'10Hz'},
                    {'label':'15 Hz','value':'15Hz'},
                    {'label':'25 Hz','value':'25Hz'},
                    {'label':'30 Hz','value':'30Hz'},
                    {'label':'50 Hz','value':'50Hz'},
                    {'label':'60 Hz','value':'60Hz'},
                    {'label':'100 Hz','value':'100Hz'},
                    {'label':'500 Hz','value':'500Hz'},
                    {'label':'1 KHz','value':'1KHz'},
                    {'label':'2 KHz','value':'2KHz'},
                    {'label':'3.75 KHz','value':'3.75Hz'},
                    {'label':'7.5 KHz','value':'7.5KHz'},
                    {'label':'15 KHz','value':'15KHz'},
                    {'label':'30 KHz','value':'30KHz'}
                    ]
                ),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='samplefreq_input',
                       children=['Sampling Frequency'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('samplefreq_input_value_update_acknowledged','data'),
    [Input('samplefreq_input','value')],
    [State('samplefreq_input_value_update','data'),
     State('samplefreq_input_value_update_acknowledged','data')])
def update_samplefreq(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'samplefreq_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def iv_gain():
    return html.Div(id='iv_gain_input_container',
        className='centered_row',
        children=[
            dcc.Store(id='iv_gain_input_value_update', data=1),
            dcc.Store(id='iv_gain_input_value_update_acknowledged', data=2),
            dcc.Dropdown(
                id='iv_gain_input',
                clearable=False,
                style={'width':'65px','color':'black','fontSize':'x-small'},
                options=[
                    {'label':'0 Ω','value':'POT_GAIN_0'},
                    {'label':'100 Ω','value':'POT_GAIN_0'},
                    {'label':'3 KΩ','value':'POT_GAIN_3K'},
                    {'label':'30 KΩ','value':'POT_GAIN_30K'},
                    {'label':'300 KΩ','value':'POT_GAIN_300K'},
                    {'label':'3 MΩ','value':'POT_GAIN_3M'},
                    {'label':'30 MΩ','value':'POT_GAIN_30M'},
                    {'label':'100 MΩ','value':'POT_GAIN_100M'}
                    ]
                ),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='iv_gain_input',
                       children=['IV Gain'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('iv_gain_input_value_update_acknowledged','data'),
    [Input('iv_gain_input','value')],
    [State('iv_gain_input_value_update','data'),
     State('iv_gain_input_value_update_acknowledged','data')])
def update_iv_gain(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'iv_gain_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def pga_gain():
    return html.Div(id='pga_gain_input_container',
        className='centered_row',
        children=[
            dcc.Store(id='pga_gain_input_value_update', data=1),
            dcc.Store(id='pga_gain_input_value_update_acknowledged', data=2),
            dcc.Dropdown(
                id='pga_gain_input',
                style={'width':'65px','color':'black'},
                clearable=False,
                options=[
                    {'label':'1 X','value':1},
                    {'label':'2 X','value':2},
                    {'label':'4 X','value':4},
                    {'label':'8 X','value':8},
                    {'label':'16 X','value':16}
                    ]
                ),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='pga_gain_input',
                       children=['PGA Gain'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('pga_gain_input_value_update_acknowledged','data'),
    [Input('pga_gain_input','value')],
    [State('pga_gain_input_value_update','data'),
     State('pga_gain_input_value_update_acknowledged','data')])
def update_pga_gain(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'pga_gain_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def n_scans():
    return html.Div(id='n_scans_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='n_scans_input',
                        min=0,
                        max=100,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='n_scans_input_value_update', data=1),
            dcc.Store(id='n_scans_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='n_scans_input',
                       children=['Number',html.Br(),'of Scans'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('n_scans_input_value_update_acknowledged','data'),
    [Input('n_scans_input','value')],
    [State('n_scans_input_value_update','data'),
     State('n_scans_input_value_update_acknowledged','data')])
def update_n_scans(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'n_scans_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def plating_potential():
    return html.Div(id='plating_potential_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='plating_potential_input',
                        min=-1999,
                        max=1999,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='plating_potential_input_value_update', data=1),
            dcc.Store(id='plating_potential_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='plating_potential_input',
                       children=['Plating',html.Br(),'Potential [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('plating_potential_input_value_update_acknowledged','data'),
    [Input('plating_potential_input','value')],
    [State('plating_potential_input_value_update','data'),
     State('plating_potential_input_value_update_acknowledged','data')])
def update_plating_potential(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'plating_potential_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
        
def plating_time():
    return html.Div(id='plating_time_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='plating_time_input',
                        min=0,
                        max=1200,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='plating_time_input_value_update', data=1),
            dcc.Store(id='plating_time_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='plating_time_input',
                       children=['Plating',html.Br(),'Time [s]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('plating_time_input_value_update_acknowledged','data'),
    [Input('plating_time_input','value')],
    [State('plating_time_input_value_update','data'),
     State('plating_time_input_value_update_acknowledged','data')])
def update_plating_time(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'plating_time_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update
   
def comment():
    return html.Div(id='comment_input_container',
        className='centered_row',
        style={'width':'185px'},
        children=[
            dcc.Input(id='comment_input',
                placeholder='Comment',
                type='text',
                style={'backgroundColor':'transparent','color':'rgb(200, 200, 200)','width':'185px'},
                debounce=True
                ),
            dcc.Store(id='comment_input_value_update', data=1),
            dcc.Store(id='comment_input_value_update_acknowledged', data=2),
            ]
        )
@app.callback(
    Output('comment_input_value_update_acknowledged','data'),
    [Input('comment_input','value')],
    [State('comment_input_value_update','data'),
     State('comment_input_value_update_acknowledged','data')])
def update_comment(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'comment_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update

def n_electrode_tests():
    return html.Div(id='n_electrode_tests_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'65px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='n_electrode_tests_input',
                        min=0,
                        max=100,
                        size=65
                        )
                    )
                ),
            dcc.Store(id='n_electrode_tests_input_value_update', data=1),
            dcc.Store(id='n_electrode_tests_input_value_update_acknowledged', data=2),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='n_electrode_tests_input',
                       children=['Test',html.Br(),'Scans'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    Output('n_electrode_tests_input_value_update_acknowledged','data'),
    [Input('n_electrode_tests_input','value')],
    [State('n_electrode_tests_input_value_update','data'),
     State('n_electrode_tests_input_value_update_acknowledged','data')])
def update_n_electrode_tests(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'n_electrode_tests_input',
                       'attribute':'value','value':value}])
        raise PreventUpdate
    else:
        return update