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
        id='single_CV_interval',
        interval=250, # in milliseconds
        n_intervals=0
        ),
        dcc.Store(id='single_CV_timestamp', data=1),
        
        html.Div(
            className='sub_program',
            children=[
                dcc.Store(id='single_CV_graph_file'),
                dcc.Graph(id='single_CV_graph')
                ]
            ),
        
        html.Div(
            className='sub_program',
            children=[
                html.Div(
                    className='centered_row',
                    children=html.H5('Status')
                    ),
                html.Div(
                    className='centered_row',
                    children=[
                        html.Label(htmlFor='single_CV_purge_indicator',children='Purge'),
                        html.Div(style={'width':'5px'}),
                        daq.Indicator(id="single_CV_purge_indicator",size=20),
                        
                        html.Div(style={'width':'15px'}),
                        
                        html.Label(htmlFor='single_CV_stirr_indicator',children='Stirring'),
                        html.Div(style={'width':'5px'}),
                        daq.Indicator(id="single_CV_stirr_indicator",size=20),
                        
                        html.Div(style={'width':'15px'}),
                        
                        html.Label(htmlFor='single_CV_scan_indicator',children='Scan'),
                        html.Div(style={'width':'5px'}),
                        daq.Indicator(id='single_CV_scan_indicator',size=20)
                        ]
                    )
                ]
            ),
        
        html.Div(
            className='sub_program',
            children=[
                html.Div(
                    className='centered_row',
                    children=[
                        html.Button(
                            id='single_CV_start_button',
                            children='Start Measurement',
                            style={'width':'30%'}
                            ),
                        dcc.Store('single_CV_start_popup_placeholder1'),
                        dcc.Store('single_CV_start_popup_placeholder2'),
                        dbc.Modal(
                            [
                                dbc.ModalHeader("Start Measurement"),
                                dbc.ModalBody(
                                    children=[
                                        dcc.Input(
                                            id='single_CV_scan_id',
                                            placeholder='Scan ID',
                                            type='text')
                                        ]),
                                dbc.ModalFooter(
                                    children = html.Button("Go!", id="single_CV_start_button_go")
                                    )
                                
                            ],
                            id='single_CV_start_popup',
                            centered=True),
                        
                        html.Div(style={'width':'10px'}),
                        daq.GraduatedBar(
                            id='single_CV_progress_bar',
                            min=0,
                            max=100,
                            step=5,
                            showCurrentValue=True,
                            size=200
                            ),
                        html.Div(style={'width':'10px'}),
                        dcc.Store(id='single_CV_cancel_button_placeholder'),
                        html.Button(
                            id='single_CV_cancel_button',
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
                            children=daq.BooleanSwitch(id="single_CV_stirr_switch")),
                        html.Label(
                            htmlFor='single_CV_stirr_switch',
                            children='Stirring',
                            style={'width':'100px'}),
                        dcc.Store(id='single_CV_stirr_switch_update', data=1),
                        dcc.Store(id='single_CV_stirr_switch_update_acknowledged', data=2),
                        
                        daq.Slider(
                            id='single_CV_stirr_speed_slider',
                            min=200,
                            max=2500,
                            step=100,
                            handleLabel={"showCurrentValue": True,"label": "RPM"},
                            size=200
                            ),
                        dcc.Store(id='single_CV_stirr_speed_placeholder'),
                        dcc.Store(id='single_CV_stirr_speed_slider_update', data=1),
                        dcc.Store(id='single_CV_stirr_speed_slider_update_acknowledged', data=2),

                        html.Label(
                            htmlFor='single_CV_purge_switch',
                            children='Purge',
                            style={'width':'100px','textAlign':'right'}),
                        html.Div(
                            style={'width':'80px'},
                            children=daq.BooleanSwitch(id="single_CV_purge_switch")),
                        dcc.Store(id='single_CV_purge_switch_update', data=1),
                        dcc.Store(id='single_CV_purge_switch_update_acknowledged', data=2),
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
                                    id='single_CV_cleaning_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_cleaning_potential_input',
                                   children=['Cleaning',html.Br(),'Potential [mV]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='single_CV_cleaning_time_input',
                                    min=0,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_cleaning_time_input',
                                   children=['Cleaning',html.Br(),'Time [s]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='single_CV_start_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_start_potential_input',
                                   children=['Start [mV]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='single_CV_vertex2_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_vertex2_potential_input',
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
                                    id='single_CV_deposition_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_deposition_potential_input',
                                   children=['Deposition',html.Br(),'Potential [mV]'],
                                   style={'width':'110px'}),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='single_CV_deposition_time_input',
                                    min=0,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_deposition_time_input',
                                   children=['Deposition',html.Br(),'Time [s]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='single_CV_vertex1_potential_input',
                                    min=-1999,
                                    max=1999,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_vertex1_potential_input',
                                   children=['Vertex 1 [mV]'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='single_CV_slope_input',
                                    min=0,
                                    max=3000,
                                    size=65
                                    )
                                )
                            ),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_slope_input',
                                   children=['Slope [mV/s]'],
                                   style={'width':'110px'}
                                   ),
                        ]
                    ),
                html.Div(
                    className='centered_row',
                    children=[
                        dcc.Store(id='single_CV_samplefreq_input_update', data=1),
                        dcc.Store(id='single_CV_samplefreq_input_update_acknowledged', data=2),
                        dcc.Dropdown(
                            id='single_CV_samplefreq_input',
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
                        html.Label(htmlFor='single_CV_samplefreq_input',
                                   children=['Sampling Frequency'],
                                   style={'width':'110px'}
                                   ),
                        dcc.Store(id='single_CV_iv_gain_input_update', data=1),
                        dcc.Store(id='single_CV_iv_gain_input_update_acknowledged', data=2),
                        dcc.Dropdown(
                            id='single_CV_iv_gain_input',
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
                        html.Label(htmlFor='single_CV_iv_gain_input',
                                   children=['IV Gain'],
                                   style={'width':'110px'}
                                   ),
                        dcc.Store(id='single_CV_PGA_gain_input_update', data=1),
                        dcc.Store(id='single_CV_PGA_gain_input_update_acknowledged', data=2),
                        dcc.Dropdown(
                            id='single_CV_PGA_gain_input',
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
                        html.Label(htmlFor='single_CV_PGA_gain_input',
                                   children=['PGA Gain'],
                                   style={'width':'110px'}
                                   ),
                        html.Div(
                            style={'width':'65px'},
                            children=daq.DarkThemeProvider(
                                theme=light_theme,
                                children=daq.NumericInput(
                                    id='single_CV_n_scans_input',
                                    min=0,
                                    size=65
                                    )
                                )),
                        html.Div(style={'width':'10px'}),
                        html.Label(htmlFor='single_CV_n_scans_input',
                                   children=['Number',html.Br(),'of scans'],
                                   style={'width':'110px'}
                                   )
                            
                        ]
                    )
                                
                ]
            )
        ]

@app.callback(
    Output('single_CV_graph','figure'),
    [Input('single_CV_graph_file','data')])
def update_graph(file):
    df=pd.read_csv(file)
    config = literal_eval(str(root.single_CV))
    graph_title = config['start_button_go']['scan_id']
    figure={
        'data':[{'x':df.potential,
                 'y':df.current,
                 'marker':{'color':'rgb(155,240,255)'}
                 }
                ],
        'layout':{
            'title':{
                'text':graph_title,
                'font':{'color':'white'}},
            'xaxis':{
                'title':{
                    'text':'Potential [mV] vs. Ag/AgCl',
                    'font':{'color':'white'}},
                'autorange':'reversed',
                'gridcolor':'black',
                'zerolinecolor':'black',
                'zerolinewidth':2,
                'tickfont':{'color':'white'}
                },
            'yaxis':{
                'title':{
                    'text':'Current [A]',
                    'font':{'color':'white'}},
                'autorange':'reversed',
                'gridcolor':'black',
                'zerolinecolor':'black',
                'zerolinewidth':2,
                'tickfont':{'color':'white'}
                },
            'paper_bgcolor':'rgba(0,0,0,0)',
            'plot_bgcolor':'rgba(0,0,0,0)'
            }
        }
    return figure

# open modal popup for the user to enter a scan id before starting a measurement
@app.callback(
    [Output('single_CV_start_popup_placeholder1','data'),
     Output('single_CV_scan_id','value')],
    [Input('single_CV_start_button','n_clicks')])
def openMeasurementPopup(n_clicks):
    if n_clicks != None:
        return ('open', '')
    else:
        raise PreventUpdate

    
# since the modal popup is opened by one button and closed by another,
# two placeholder components are used to control its open state
@app.callback(
    Output('single_CV_start_popup','is_open'),
    [Input('single_CV_start_popup_placeholder1','data'),
     Input('single_CV_start_popup_placeholder2','data')])
def open_close_popup(placeholder1,placeholder2):
    #determining which input was triggered to determine whther to open or close the modal
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if trigger_id == 'single_CV_start_popup_placeholder1':
        return True
    elif trigger_id == 'single_CV_start_popup_placeholder2':
        return False
    else:
        return False

# when the button in the modal popup is pressed, get the scn id and scan parameters and start measurement  
@app.callback(
    Output('single_CV_start_popup_placeholder2','data'),
    [Input("single_CV_start_button_go",'n_clicks')],
    [State('single_CV_scan_id','value'),
     State('single_CV_cleaning_potential_input','value'),
     State('single_CV_cleaning_time_input','value'),
     State('single_CV_deposition_potential_input','value'),
     State('single_CV_deposition_time_input','value'),
     State('single_CV_start_potential_input','value'),
     State('single_CV_vertex1_potential_input','value'),
     State('single_CV_vertex2_potential_input','value'),
     State('single_CV_slope_input','value'),
     State('single_CV_samplefreq_input','value'),
     State('single_CV_iv_gain_input','value'),
     State('single_CV_PGA_gain_input','value'),
     State('single_CV_n_scans_input','value')])
def start_measurement(n_clicks,scan_id,cleaning_potential,cleaning_time,deposition_potential,
                      deposition_time,start_potential,vertex1_potential,vertex2_potential,
                      slope,samplefreq,iv_gain,PGA_gain,n_scans):
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
             'attribute':'value', 'value':n_scans}])
        return 'close'

@app.callback(
    Output('single_CV_cancel_button_placeholder','data'),
    [Input('single_CV_cancel_button','n_clicks')])
def cancel_measurement(n_clicks):
    if n_clicks != None:
        write_config([{'component':'cancel_button','attribute':'triggered','value':True}])
    raise PreventUpdate

# start measurement by triggering button callback when scan id is submitted
@app.callback(
    Output('single_CV_start_button_go','n_clicks'),
    [Input('single_CV_scan_id','n_submit')],
    [State('single_CV_start_button_go','n_clicks')])
def start_measurement_by_submit(n_submit,n_clicks):
    if n_submit != None:
        return n_clicks+1
    
# if state of stirring switch changes, write to config file and update status indicator
@app.callback(
    [Output('single_CV_stirr_indicator','value'),
     Output('single_CV_stirr_switch_update_acknowledged','data')],
    [Input('single_CV_stirr_switch','on')],
    [State('single_CV_stirr_switch_update','data'),
     State('single_CV_stirr_switch_update_acknowledged','data')])
def control_stirring(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_switch',
                       'attribute':'on','value':switch}])
        return switch, no_update
    else:
        return switch, update

@app.callback(
    [Output('single_CV_stirr_speed_placeholder','data'),
     Output('single_CV_stirr_speed_slider_update_acknowledged','data')],
    [Input('single_CV_stirr_speed_slider','value')],
    [State('single_CV_stirr_speed_slider_update','data'),
     State('single_CV_stirr_speed_slider_update_acknowledged','data')])
def update_stirr_speed(speed, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'stirr_speed_slider',
                       'attribute':'value','value':speed}])
        raise PreventUpdate
    else:
        return no_update, update

# if state of purge switch changes, write to config file and update status indicator
@app.callback(
    [Output('single_CV_purge_indicator','value'),
     Output('single_CV_purge_switch_update_acknowledged','data')],
    [Input('single_CV_purge_switch','on')],
    [State('single_CV_purge_switch_update','data'),
     State('single_CV_purge_switch_update_acknowledged','data')])
def control_purging(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'purge_switch',
                       'attribute':'on','value':switch}])
        return switch, no_update
    else:
        return switch, update


# if sample frequency is changed, write value to config and trigger update
@app.callback(
     Output('single_CV_samplefreq_input_update_acknowledged','data'),
    [Input('single_CV_samplefreq_input','value')],
     [State('single_CV_samplefreq_input_update','data'),
      State('single_CV_samplefreq_input_update_acknowledged','data')])
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
     Output('single_CV_iv_gain_input_update_acknowledged','data'),
    [Input('single_CV_iv_gain_input','value')],
     [State('single_CV_iv_gain_input_update','data'),
      State('single_CV_iv_gain_input_update_acknowledged','data')])
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
     Output('single_CV_PGA_gain_input_update_acknowledged','data'),
    [Input('single_CV_PGA_gain_input','value')],
     [State('single_CV_PGA_gain_input_update','data'),
      State('single_CV_PGA_gain_input_update_acknowledged','data')])
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
    Output('single_CV_timestamp','data'),
    [Input('single_CV_interval','n_intervals')],
    [State('single_CV_timestamp','data')])
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
    ('n_scans_input','value')
    ]

# generating lists of parameters for callback function
update_outputs = []
update_states = []
factors = []
for parameter in update_list:
    if '§' in parameter[0]:
        parameter = (parameter[0][0:-1], parameter[1])
    update_outputs.append(Output('single_CV_' + parameter[0], parameter[1]))
    update_states.append(State('single_CV_' + parameter[0], parameter[1]))
    factors.append(parameter[0] + '_' + parameter[1])
  
@app.callback(
    update_outputs,
    [Input('single_CV_timestamp','data')],
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
