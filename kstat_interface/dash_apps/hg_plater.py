import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
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

light_theme={
    'dark': False,
    'detail': '#007439',
    'primary': '#8be3ff',
    'secondary': '#6E6E6E',
}

def main():
    return [
        dcc.Interval(
        id='hg_plater_interval',
        interval=250, # in milliseconds
        n_intervals=0
        ),
        dcc.Store(id='hg_plater_timestamp', data=1),
        
        html.Div(
            className='sub_program centered_row',
             children=[
                html.Div(
                     children=[
                        html.Div(
                            className='left_row',children=[
                            html.Div(
                                style={'width':'80px'},className='centered_row',
                                 children=daq.DarkThemeProvider(
                                     theme=light_theme,
                                    children=daq.NumericInput(
                                        id='hg_plater_plating_potential_input',
                                         min=-1999,
                                         max=1999
                                      ))),
                            html.Label(htmlFor='hg_plater_plating_potential_input',
                                       children='Plating Potential [mV]')]),
                        
                        html.Div(className='left_row',children=[
                            html.Div(
                                style={'width':'80px'},className='centered_row',
                                 children=daq.DarkThemeProvider(
                                     theme=light_theme,
                                        children=daq.NumericInput(
                                            id='hg_plater_plating_time_input',
                                               min=1,
                                               max=600
                                      ))),
                            html.Label(htmlFor='hg_plater_plating_time_input',
                                       children='Plating Time [s]')]),

                        html.Div(className='left_row',children=[
                            html.Div(
                                style={'width':'80px'},
                                 children=daq.BooleanSwitch(id="hg_plater_purge_switch")),
                            html.Label(htmlFor='hg_plater_purge_switch',children='Purge'),
                            dcc.Store(id='hg_plater_purge_switch_update', data=1),
                            dcc.Store(id='hg_plater_purge_switch_update_acknowledged', data=2)]),

                        html.Div(className='left_row',children=[
                            html.Div(
                                style={'width':'80px'},
                                 children=daq.BooleanSwitch(id="hg_plater_stirr_switch")),
                            html.Label(htmlFor='hg_plater_stirr_switch',children='Stirring'),
                            dcc.Store(id='hg_plater_stirr_switch_update', data=1),
                            dcc.Store(id='hg_plater_stirr_switch_update_acknowledged', data=2)])
                                ]),
                html.Div(style={'width':'5%'}),
                html.Div(style={'minWidth':'50%'},
                         children=[
                                html.Div(
                                style={'display':'flex','width':'100%'},
                                     children=[
                                            dcc.Store(id='hg_plater_plating_placeholder'),
                                            html.Button(id='hg_plater_plating_button',
                                                        children='Start Plating',
                                                        style={'width':'48%'}),
                                            html.Div(style={'width':'4%'}),
                                            dcc.Store(id='hg_plater_cancel_plating_placeholder'),
                                            html.Button(id='hg_plater_cancel_plating_button',
                                                        children='Cancel Plating',
                                                        style={'width':'48%'})]),

                                html.Div(
                                    style={'marginTop':'5px','marginBottom':'50px'},
                                     className='centered_row',
                                     children=daq.GraduatedBar(
                                         id='hg_plater_progress_bar',
                                         min=0,
                                         max=100,
                                         step=5,
                                         showCurrentValue=True,
                                         size=200
                                         )),
                                html.Div(
                                    className='centered_row',
                                     children=daq.Slider(
                                         id="hg_plater_stirr_speed_slider",
                                         min=200,
                                         max=2500,
                                         step=100,
                                         handleLabel={"showCurrentValue": True,"label": "RPM"},
                                         size=200
                                         )),
                                dcc.Store(id='hg_plater_stirr_speed_placeholder'),
                                dcc.Store(id='hg_plater_stirr_speed_slider_update', data=1),
                                dcc.Store(id='hg_plater_stirr_speed_update_acknowledged', data=2)])
                                ]),

    html.Div(className='sub_program',
             children=[
                 html.Div(className='centered_row',
                          children=html.H5('Status')),
                 html.Div(
                     className='centered_row',
                      children=[
                            html.Label(htmlFor='hg_plater_purge_indicator',children='Purge'),
                            html.Div(style={'width':'5px'}),
                            daq.Indicator(id="hg_plater_purge_indicator",size=20),
                            
                            html.Div(style={'width':'15px'}),
                            
                            html.Label(htmlFor='hg_plater_stirr_indicator',children='Stirring'),
                            html.Div(style={'width':'5px'}),
                            daq.Indicator(id="hg_plater_stirr_indicator",size=20),
                            
                            html.Div(style={'width':'15px'}),
                            
                            html.Label(htmlFor='hg_plater_plating_indicator',children='Plating'),
                            html.Div(style={'width':'5px'}),
                            daq.Indicator(id='hg_plater_plating_indicator',size=20)
                            ])
                 ])

    ]

# if state of stirring switch changes, write to config file and update status indicator
@app.callback(
    [Output('hg_plater_stirr_indicator','value'),
     Output('hg_plater_stirr_switch_update_acknowledged','data')],
    [Input('hg_plater_stirr_switch','on')],
    [State('hg_plater_stirr_switch_update','data'),
     State('hg_plater_stirr_switch_update_acknowledged','data')])
def control_stirring(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_switch',
                       'attribute':'on','value':switch}])
        return switch, no_update
    else:
        return switch, update

@app.callback(
    [Output('hg_plater_stirr_speed_placeholder','data'),
     Output('hg_plater_stirr_speed_update_acknowledged','data')],
    [Input('hg_plater_stirr_speed_slider','value')],
    [State('hg_plater_stirr_speed_update','data'),
     State('hg_plater_stirr_speed_update_acknowledged','data')])
def update_stirr_speed(speed, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_speed_slider',
                       'attribute':'value','value':speed}])
        raise PreventUpdate
    else:
        return no_update, update

# if state of purge switch changes, write to config file and update status indicator
@app.callback(
    [Output('hg_plater_purge_indicator','value'),
     Output('hg_plater_purge_switch_update_acknowledged','data')],
    [Input('hg_plater_purge_switch','on')],
    [State('hg_plater_purge_switch_update','data'),
     State('hg_plater_purge_switch_update_acknowledged','data')])
def control_purging(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'purge_switch',
                       'attribute':'on','value':switch}])
        return switch, no_update
    else:
        return switch, update

# start plating procedure on button input
@app.callback(
    Output('hg_plater_plating_placeholder','data'),
    [Input('hg_plater_plating_button','n_clicks')],
    [State('hg_plater_plating_potential_input','value'),
     State('hg_plater_plating_time_input','value')])
def start_plating(n_clicks,plating_potential,plating_time):
    if n_clicks != None:
        write_config([{'component':'plating_button',
                       'attribute':'triggered','value':True},
                      {'component':'plating_potential_input',
                       'attribute':'value','value':plating_potential},
                      {'component':'plating_time_input',
                       'attribute':'value','value':plating_time}])
        raise PreventUpdate
    else:
        raise PreventUpdate

# cancel plating procedure on button input
@app.callback(
    Output('hg_plater_cancel_plating_placeholder','data'),
    [Input('hg_plater_cancel_plating_button','n_clicks')])
def cancel_plating(n_clicks):
    if n_clicks != None:
        write_config([{'component':'cancel_plating_button',
                       'attribute':'triggered','value':True}])
        raise PreventUpdate
    else:
        raise PreventUpdate


####################################################################
# Getting Changes from Backend
####################################################################

# check if timestamp of redis server changed to trigger config update
@app.callback(
    Output('hg_plater_timestamp','data'),
    [Input('hg_plater_interval','n_intervals')],
    [State('hg_plater_timestamp','data')])
def check_update(n_intervals, stored_stamp):
    # get time stamp of config in redis server
    try:
        root.flush()
        program = str(root.program)
        config_stamp = literal_eval(str(root[program+'_timestamp']))
    except Exception as e:
        print("Couldn't load config time stamp.", e)
        raise PreventUpdate
    # if stored time stamp matches config, no update is necessary
    # otherwise get config from redis server
    if config_stamp == stored_stamp:
        raise PreventUpdate
    else:
        return config_stamp

# add § to parameter with an update placeholder (components that have a callback based on user input).
# update placeholder needs to follow value variable
update_list=[
    ('stirr_switch§','on'),
    ('stirr_switch_update','data'),
    ('stirr_switch','disabled'),
    ('stirr_speed_slider§','value'),
    ('stirr_speed_slider_update','data'),
    ('stirr_speed_slider','disabled'),
    ('purge_switch§','on'),
    ('purge_switch_update','data'),
    ('purge_switch','disabled'),
    ('plating_potential_input','value'),
    ('plating_potential_input','disabled'),
    ('plating_time_input','value'),
    ('plating_time_input','disabled'),
    ('plating_button','disabled'),
    ('cancel_plating_button','disabled'),
    ('plating_indicator','value'),
    ('progress_bar','value')
    ]

# generating lists of parameters for callback function
update_outputs = []
update_states = []
factors = []
for parameter in update_list:
    if '§' in parameter[0]:
        parameter = (parameter[0][0:-1], parameter[1])
    update_outputs.append(Output('hg_plater_' + parameter[0], parameter[1]))
    update_states.append(State('hg_plater_' + parameter[0], parameter[1]))
    factors.append(parameter[0] + '_' + parameter[1])

@app.callback(
    update_outputs,
    [Input('hg_plater_timestamp','data')],
    update_states)
def update_config(timestamp,*factors):
    try:
        root.flush()
        program = str(root.program)
        config = literal_eval(str(root[program]))
    except Exception as e:   
        print("Couldn't load config.", e)
        #rewriting a value to config server to trigger another update
        write_config([{'component':'placeholder','attribute':'on','value':True}])
        raise PreventUpdate

    factors = list(factors)
    for i in range(len(factors)):
        if 'update' in update_list[i][0]:
            continue
        else:
            if '§' in update_list[i][0]:
                # compare configuration value to current state of component and update if there's a difference
                config_value = config[update_list[i][0][0:-1]][update_list[i][1]]
                if config_value != factors[i] and config_value != None:
                    factors[i] = config_value
                    factors[i+1] = factors[i+1] + 1
                else:
                    factors[i] = no_update
                    factors[i+1] = no_update
            else:
                config_value = config[update_list[i][0]][update_list[i][1]]
                if config_value != factors[i] and config_value != None:
                    factors[i] = config_value
                else:
                    factors[i] = no_update
    return tuple(factors)
