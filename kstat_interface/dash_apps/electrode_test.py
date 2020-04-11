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
from .status_components import status_indicator_leds
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
    return [
        dcc.Interval(
        id='electrode_test_interval',
        interval=250, # in milliseconds
        n_intervals=0
        ),
        dcc.Store(id='electrode_test_timestamp', data=1),
        
        plot_scan(),
        
        status_indicator_leds(),
        
        html.Div(
            className='sub_program',
            children=[
                html.Div(
                    className='centered_row',
                    children=[
                        html.Button(
                            id='electrode_test_start_button',
                            children='Start Measurement',
                            style={'width':'30%'}
                            ),
                        dcc.Store('electrode_test_start_popup_placeholder1'),
                        dcc.Store('electrode_test_start_popup_placeholder2'),
                        dbc.Modal(
                            [
                                dbc.ModalHeader("Start Measurement"),
                                dbc.ModalBody(
                                    children=html.Div(
                                        className='centered_row',
                                        children=[
                                            dcc.Input(
                                                id='electrode_test_scan_id',
                                                placeholder='Scan ID',
                                                type='text'),
                                            html.Div(style={'width':'10px'}),
                                            daq.DarkThemeProvider(
                                                theme=light_theme,
                                                children=daq.NumericInput(
                                                    id='electrode_test_n_blanks_input',
                                                    min=0,
                                                    size=65
                                                    )),
                                            html.Div(style={'width':'10px'}),
                                            html.Label(
                                                htmlFor='electrode_test_n_blanks_input',
                                                children='Number of Blanks',
                                                style={'width':'100px'})
                                            ]
                                        )),
                                dbc.ModalFooter(
                                    children = html.Button("Go!", id="electrode_test_start_button_go")
                                    ) 
                            ],
                            id='electrode_test_start_popup',
                            centered=True),
                        
                        html.Div(style={'width':'10px'}),
                        daq.GraduatedBar(
                            id='electrode_test_progress_bar',
                            min=0,
                            max=100,
                            step=5,
                            showCurrentValue=True,
                            size=200
                            ),
                        html.Div(style={'width':'10px'}),
                        dcc.Store(id='electrode_test_cancel_button_placeholder'),
                        html.Button(
                            id='electrode_test_cancel_button',
                            children='Cancel Measurement',
                            style={'width':'30%'}
                            ),
                        ]
                    ),
                html.Div(style={'height':'50px'}),
                html.Div(
                    className='centered_row',
                    children=[
                        html.Div(
                            style={'width':'80px'},
                            children=daq.BooleanSwitch(id="electrode_test_stirr_switch")),
                        html.Label(
                            htmlFor='electrode_test_stirr_switch',
                            children='Stirring',
                            style={'width':'100px'}),
                        dcc.Store(id='electrode_test_stirr_switch_update', data=1),
                        dcc.Store(id='electrode_test_stirr_switch_update_acknowledged', data=2),
                        
                        daq.Slider(
                            id='electrode_test_stirr_speed_slider',
                            min=200,
                            max=2500,
                            step=100,
                            handleLabel={"showCurrentValue": True,"label": "RPM"},
                            size=200
                            ),
                        dcc.Store(id='electrode_test_stirr_speed_placeholder'),
                        dcc.Store(id='electrode_test_stirr_speed_slider_update', data=1),
                        dcc.Store(id='electrode_test_stirr_speed_slider_update_acknowledged', data=2),

                        html.Label(
                            htmlFor='electrode_test_purge_switch',
                            children='Purge',
                            style={'width':'100px','textAlign':'right'}),
                        html.Div(
                            style={'width':'80px'},
                            children=daq.BooleanSwitch(id="electrode_test_purge_switch")),
                        dcc.Store(id='electrode_test_purge_switch_update', data=1),
                        dcc.Store(id='electrode_test_purge_switch_update_acknowledged', data=2),
                        ]
                    ),
                ]
            ),
        
        html.Div(
            className='sub_program',
            children=[
                html.Div(
                    className='centered_row',
                    children=html.H5('Scan Settings')),
                html.Div(
                    className='centered_row',
                    children=[
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_cleaning_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_cleaning_potential_input',
                                   children=['Cleaning',html.Br(),'Potential [mV]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_cleaning_time_input',
                                    min=0,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_cleaning_time_input',
                                   children=['Cleaning',html.Br(),'Time [s]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_start_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_start_potential_input',
                                   children=['Start [mV]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_vertex2_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_vertex2_potential_input',
                                   children=['Vertex 2 [mV]'],
                                   style={'width':'110px'}
                                   ),
                        ]
                    ),
                
                html.Div(
                    className='centered_row',
                    children=[
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_deposition_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_deposition_potential_input',
                                   children=['Deposition',html.Br(),'Potential [mV]'],
                                   style={'width':'110px'}),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_deposition_time_input',
                                    min=0,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_deposition_time_input',
                                   children=['Deposition',html.Br(),'Time [s]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_vertex1_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_vertex1_potential_input',
                                   children=['Vertex 1 [mV]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_slope_input',
                                    min=0,
                                    max=3000,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_slope_input',
                                   children=['Slope [mV/s]'],
                                   style={'width':'110px'}
                                   ),
                        ]
                    ),
                html.Div(
                    className='centered_row',
                    children=[
                        dcc.Store(id='electrode_test_samplefreq_input_update', data=1),
                        dcc.Store(id='electrode_test_samplefreq_input_update_acknowledged', data=2),
                        dcc.Dropdown(
                            id='electrode_test_samplefreq_input',
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
                        html.Label(htmlFor='electrode_test_samplefreq_input',
                                   children=['Sampling Frequency'],
                                   style={'width':'110px'}
                                   ),
                        dcc.Store(id='electrode_test_iv_gain_input_update', data=1),
                        dcc.Store(id='electrode_test_iv_gain_input_update_acknowledged', data=2),
                        dcc.Dropdown(
                            id='electrode_test_iv_gain_input',
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
                        html.Label(htmlFor='electrode_test_iv_gain_input',
                                   children=['IV Gain'],
                                   style={'width':'110px'}
                                   ),
                        dcc.Store(id='electrode_test_PGA_gain_input_update', data=1),
                        dcc.Store(id='electrode_test_PGA_gain_input_update_acknowledged', data=2),
                        dcc.Dropdown(
                            id='electrode_test_PGA_gain_input',
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
                        html.Label(htmlFor='electrode_test_PGA_gain_input',
                                   children=['PGA Gain'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='electrode_test_n_scans_input',
                                    min=0,
                                    size=65
                                    )
                                )),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='electrode_test_n_scans_input',
                                   children=['Number',html.Br(),'of scans'],
                                   style={'width':'110px'}
                                   )
                            
                        ]
                    )
                                
                ]
            )
        ]


# open modal popup for the user to enter a scan id before starting a measurement
@app.callback(
    [Output('electrode_test_start_popup_placeholder1','data'),
     Output('electrode_test_scan_id','value')],
    [Input('electrode_test_start_button','n_clicks')])
def openMeasurementPopup(n_clicks):
    if n_clicks != None:
        return ('open', '')
    else:
        raise PreventUpdate
    
# since the modal popup is opened by one button and closed by another,
# two placeholder components are used to control its open state
@app.callback(
    Output('electrode_test_start_popup','is_open'),
    [Input('electrode_test_start_popup_placeholder1','data'),
     Input('electrode_test_start_popup_placeholder2','data')])
def open_close_start_popup(placeholder1,placeholder2):
    #determining which input was triggered to determine whther to open or close the modal
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if trigger_id == 'electrode_test_start_popup_placeholder1':
        return True
    elif trigger_id == 'electrode_test_start_popup_placeholder2':
        return False
    else:
        return False

# when the button in the modal popup is pressed, get the scn id and scan parameters and start measurement  
@app.callback(
    Output('electrode_test_start_popup_placeholder2','data'),
    [Input("electrode_test_start_button_go",'n_clicks')],
    [State('electrode_test_scan_id','value'),
     State('electrode_test_cleaning_potential_input','value'),
     State('electrode_test_cleaning_time_input','value'),
     State('electrode_test_deposition_potential_input','value'),
     State('electrode_test_deposition_time_input','value'),
     State('electrode_test_start_potential_input','value'),
     State('electrode_test_vertex1_potential_input','value'),
     State('electrode_test_vertex2_potential_input','value'),
     State('electrode_test_slope_input','value'),
     State('electrode_test_samplefreq_input','value'),
     State('electrode_test_iv_gain_input','value'),
     State('electrode_test_PGA_gain_input','value'),
     State('electrode_test_n_scans_input','value'),
     State('electrode_test_n_blanks_input','value')])
def start_measurement(n_clicks,scan_id,cleaning_potential,cleaning_time,deposition_potential,
                      deposition_time,start_potential,vertex1_potential,vertex2_potential,
                      slope,samplefreq,iv_gain,PGA_gain,n_scans,n_blanks):
    if n_clicks == None:
        raise PreventUpdate
    else:
        if scan_id == None or scan_id == '':
            raise PreventUpdate
        write_config([
            {'component':'start_button_go', 'attribute':'triggered', 'value':True},
            {'component':'start_button_go', 'attribute':'scan_id', 'value':scan_id},
            {'component':'cleaning_potential_input',
             'attribute':'value', 'value':cleaning_potential},
            {'component':'cleaning_time_input',
             'attribute':'value', 'value':cleaning_time},
            {'component':'deposition_potential_input',
             'attribute':'value', 'value':deposition_potential},
            {'component':'deposition_time_input',
             'attribute':'value', 'value':deposition_time},
            {'component':'start_potential_input',
             'attribute':'value', 'value':start_potential},
            {'component':'vertex1_potential_input',
             'attribute':'value', 'value':vertex1_potential},
            {'component':'vertex2_potential_input',
             'attribute':'value', 'value':vertex2_potential},
            {'component':'slope_input',
             'attribute':'value', 'value':slope},
            {'component':'samplefreq_input',
             'attribute':'value', 'value':samplefreq},
            {'component':'iv_gain_input',
             'attribute':'value', 'value':iv_gain},
            {'component':'PGA_gain_input',
             'attribute':'value', 'value':PGA_gain},
            {'component':'n_scans_input',
             'attribute':'value', 'value':n_scans},
            {'component':'n_blanks_input',
             'attribute':'value', 'value':n_blanks}])
        return 'close'

@app.callback(
    Output('electrode_test_cancel_button_placeholder','data'),
    [Input('electrode_test_cancel_button','n_clicks')])
def cancel_measurement(n_clicks):
    if n_clicks != None:
        write_config([{'component':'cancel_button','attribute':'triggered','value':True}])
    raise PreventUpdate

  
# start measurement by triggering button callback when scan id is submitted
@app.callback(
    Output('electrode_test_start_button_go','n_clicks'),
    [Input('electrode_test_scan_id','n_submit')],
    [State('electrode_test_start_button_go','n_clicks')])
def start_measurement_by_submit(n_submit,n_clicks):
    if n_submit != None:
        if n_clicks != None:
            return n_clicks+1
        else:
            return 1
    
# if state of stirring switch changes, write to config file and update status indicator
@app.callback(
    [Output('electrode_test_stirr_indicator','value'),
     Output('electrode_test_stirr_switch_update_acknowledged','data')],
    [Input('electrode_test_stirr_switch','on')],
    [State('electrode_test_stirr_switch_update','data'),
     State('electrode_test_stirr_switch_update_acknowledged','data')])
def control_stirring(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_switch',
                       'attribute':'on','value':switch}])
        return switch, no_update
    else:
        return switch, update

@app.callback(
    [Output('electrode_test_stirr_speed_placeholder','data'),
     Output('electrode_test_stirr_speed_slider_update_acknowledged','data')],
    [Input('electrode_test_stirr_speed_slider','value')],
    [State('electrode_test_stirr_speed_slider_update','data'),
     State('electrode_test_stirr_speed_slider_update_acknowledged','data')])
def update_stirr_speed(speed, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_speed_slider',
                       'attribute':'value','value':speed}])
        raise PreventUpdate
    else:
        return no_update, update

# if state of purge switch changes, write to config file and update status indicator
@app.callback(
    [Output('electrode_test_purge_indicator','value'),
     Output('electrode_test_purge_switch_update_acknowledged','data')],
    [Input('electrode_test_purge_switch','on')],
    [State('electrode_test_purge_switch_update','data'),
     State('electrode_test_purge_switch_update_acknowledged','data')])
def control_purging(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'purge_switch',
                       'attribute':'on','value':switch}])
        return switch, no_update
    else:
        return switch, update


# if sample frequency is changed, write value to config and trigger update
@app.callback(
     Output('electrode_test_samplefreq_input_update_acknowledged','data'),
    [Input('electrode_test_samplefreq_input','value')],
     [State('electrode_test_samplefreq_input_update','data'),
      State('electrode_test_samplefreq_input_update_acknowledged','data')])
def set_samplefreq(value,update,update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'samplefreq_input',
                       'attribute':'value','value':value},
                      {'component':'samplefreq_input',
                       'attribute':'triggered','value':True}])
        return no_update
    else:
        return update
    
# if IV gain is changed, write value to config and trigger update
@app.callback(
     Output('electrode_test_iv_gain_input_update_acknowledged','data'),
    [Input('electrode_test_iv_gain_input','value')],
     [State('electrode_test_iv_gain_input_update','data'),
      State('electrode_test_iv_gain_input_update_acknowledged','data')])
def set_iv_gain(value,update,update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'iv_gain_input',
                       'attribute':'value','value':value},
                      {'component':'iv_gain_input',
                       'attribute':'triggered','value':True}])
        return no_update
    else:
        return update

# if PGA gain is changed, write value to config and trigger update
@app.callback(
     Output('electrode_test_PGA_gain_input_update_acknowledged','data'),
    [Input('electrode_test_PGA_gain_input','value')],
     [State('electrode_test_PGA_gain_input_update','data'),
      State('electrode_test_PGA_gain_input_update_acknowledged','data')])
def set_PGA_gain(value,update,update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'PGA_gain_input',
                       'attribute':'value','value':value},
                      {'component':'PGA_gain_input',
                       'attribute':'triggered','value':True}])
        return no_update
    else:
        return update

####################################################################
# Getting Changes from Backend
####################################################################

# check if timestamp of redis server changed to trigger config update
@app.callback(
    Output('electrode_test_timestamp','data'),
    [Input('electrode_test_interval','n_intervals')],
    [State('electrode_test_timestamp','data')])
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
    ('progress_bar','value'),
    ('scan_indicator','value'),
    ('cleaning_potential_input','value'),
    ('cleaning_time_input','value'),
    ('deposition_potential_input','value'),
    ('deposition_time_input','value'),
    ('start_potential_input','value'),
    ('vertex1_potential_input','value'),
    ('vertex2_potential_input','value'),
    ('slope_input','value'),
    ('start_button','disabled'),
    ('cancel_button','disabled'),
    ('graph_file','data'),
    ('samplefreq_input§','value'),
    ('samplefreq_input_update','data'),
    ('iv_gain_input§','value'),
    ('iv_gain_input_update','data'),
    ('PGA_gain_input§','value'),
    ('PGA_gain_input_update','data'),
    ('n_scans_input','value'),
    ('n_blanks_input','value')
    ]

# generating lists of parameters for callback function
update_outputs = []
update_states = []
factors = []
for parameter in update_list:
    if '§' in parameter[0]:
        parameter = (parameter[0][0:-1], parameter[1])
    update_outputs.append(Output('electrode_test_' + parameter[0], parameter[1]))
    update_states.append(State('electrode_test_' + parameter[0], parameter[1]))
    factors.append(parameter[0] + '_' + parameter[1])
  
@app.callback(
    update_outputs,
    [Input('electrode_test_timestamp','data')],
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
