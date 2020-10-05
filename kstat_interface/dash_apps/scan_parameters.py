# GUI Frontend for the KStat electrochemical analyzer
# Collapsable Block to display scan parameters for voltammetric measurements underneath plot
# using Dash by Plotly (MIT licensed)
# Nico Fröhberg, 2020
# nico.froehberg@gmx.de

from time import time
from datetime import datetime
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import no_update, callback_context
from redisworks import Root
from .. import redis_config
from .app import app, write_config
from ast import literal_eval
from time import time

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

light_theme={
    'dark': False,
    'detail': '#007439',
    'primary': '#8be3ff',
    'secondary': '#6E6E6E',
}

def scan_parameters():
    return html.Div(id='scan_parameters',
        children=[
            html.Div(className='centered_row',
                children=[
                    noise_filter(),
                    html.Button(children='Scan Parameters',
                        id='scan_parameters_button',
                        style={'width':'250px','fontSize':'xx-small','border': '1px solid #bbb','lineHeight': '20px'}),
                    html.Div(style={'width':'5px'}),
                    html.Button(children='Peak Detection',
                        id='peak_detection_button',
                        style={'width':'250px','fontSize':'xx-small','border': '1px solid #bbb','lineHeight': '20px'}),
                    html.Div(style={'width':'5px'}),
                    html.Button(children='Oxygen Measurement',
                        id='o2_measurement_button',
                        style={'width':'250px','fontSize':'xx-small','border': '1px solid #bbb','lineHeight': '20px'}),
                    ]),
            dbc.Collapse(id='scan_parameters_collapse',
                        children=html.Button(id='copy_scan_settings_button',children='Copy Scan Parameters to Current Settings')),
            dbc.Collapse(id='peak_detection_collapse',
                className='left_row',
                children=[
                    peak_detection_switch(),
                    manual_peak_detection(),
                    baseline_switch(),
                    baseline_polynomial(),
                    peak_distance(),
                    peak_threshold(),
                    peak_width(),
                    html.Button(id='save_peak_button',children='Save Peak(s)',
                        style={'width':'225px'}),
                    dbc.Tooltip('Saves manually and/or automatically determined peaks to file, depending which is active',
                        target='save_peak_button'),
                    dcc.Store(id='peak_file_data',data=''),
                    dcc.Store(id='peak_file_placeholder'),
                    ]),
            dbc.Collapse(id='o2_measurement_collapse',
                className='left_row',
                children=[
                    o2_measurement_switch(),
                    o2_lower_left(),
                    o2_lower_right(),
                    o2_upper_left(),
                    o2_upper_right()])
                ])

@app.callback(
    Output('voltammogram_graph_file4','data'),
    [Input('peak_threshold_input_graph_update','modified_timestamp'),
     Input('peak_threshold_range_graph_update','modified_timestamp'),
     Input('peak_distance_input_graph_update','modified_timestamp'),
     Input('baseline_polynomial_input_graph_update','modified_timestamp'),
     Input('baseline_switch_graph_update','modified_timestamp'),
     Input('peak_detection_switch_graph_update','modified_timestamp'),
     Input('peak_width_input_graph_update','modified_timestamp'),
     Input('o2_upper_right_input_graph_update','modified_timestamp'),
     Input('o2_upper_left_input_graph_update','modified_timestamp'),
     Input('o2_lower_right_input_graph_update','modified_timestamp'),
     Input('o2_lower_left_input_graph_update','modified_timestamp'),
     Input('o2_measurement_switch_graph_update','modified_timestamp'),])
def update_graph_peak(input1,input2,input3,input4,input5,input6,input7,input8,input9,input10,input11,input12):
    return time()

@app.callback(
     Output('peak_file_placeholder','data'),
    [Input('save_peak_button','n_clicks')],
    [State('peak_file_data','data')])
def save_peak_data(n_clicks,data):
    if n_clicks != None:
        if data != '':
            f = open(data[0],'w')
            f.write(data[1])
            f.close()
    raise PreventUpdate

def peak_threshold():
    return html.Div(id='peak_threshold_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'50px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='peak_threshold_input',
                        min=1,
                        max=999,
                        size=50
                        )
                    )
                ),
            dcc.Store(id='peak_threshold_input_value_update', data=1),
            dcc.Store(id='peak_threshold_input_value_update_acknowledged', data=2),
            dcc.Store(id='peak_threshold_input_graph_update'),
            dcc.Store(id='peak_threshold_range_value_update', data=1),
            dcc.Store(id='peak_threshold_range_value_update_acknowledged', data=2),
            dcc.Store(id='peak_threshold_range_graph_update'),
            html.Div(style={'width':'5px'}),
            dcc.Dropdown(
                id='peak_threshold_range',
                style={'width':'40px','color':'black','fontSize':'x-small'},
                clearable=False,
                options=[
                    {'label':'A','value':1},
                    {'label':'mA','value':1000},
                    {'label':'µA','value':1000000},
                    {'label':'nA','value':1000000000},
                    {'label':'pA','value':1000000000000},
                    {'label':'fA','value':1000000000000000},
                    ]
                ),
            dbc.Tooltip('minimum peak current for detection (baseline removed)',
                target='peak_threshold_input'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='peak_threshold_input',
                       children=['Peak',html.Br(),'Threshold'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('peak_threshold_input_value_update_acknowledged','data'),
     Output('peak_threshold_input_graph_update','data')],
    [Input('peak_threshold_input','value')],
    [State('peak_threshold_input_value_update','data'),
     State('peak_threshold_input_value_update_acknowledged','data')])
def update_peak_threshold(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'peak_threshold_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]
@app.callback(
    [Output('peak_threshold_range_value_update_acknowledged','data'),
     Output('peak_threshold_range_graph_update','data')],
    [Input('peak_threshold_range','value')],
    [State('peak_threshold_range_value_update','data'),
     State('peak_threshold_range_value_update_acknowledged','data')])
def update_peak_range(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'peak_threshold_range',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]

def peak_width():
    return html.Div(id='peak_width_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'95px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='peak_width_input',
                        min=0,
                        max=1999,
                        size=95
                        )
                    )
                ),
            dbc.Tooltip('range around peak value used for Gaussian fitting (refinement of peak location)',
                target='peak_width_input'),
            dcc.Store(id='peak_width_input_value_update', data=1),
            dcc.Store(id='peak_width_input_value_update_acknowledged', data=2),
            dcc.Store(id='peak_width_input_graph_update'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='peak_width_input',
                       children=['Peak',html.Br(),'Width [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('peak_width_input_value_update_acknowledged','data'),
     Output('peak_width_input_graph_update','data')],
    [Input('peak_width_input','value')],
    [State('peak_width_input_value_update','data'),
     State('peak_width_input_value_update_acknowledged','data')])
def update_peak_width(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'peak_width_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]

def peak_distance():
    return html.Div(id='peak_distance_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'95px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='peak_distance_input',
                        min=0,
                        max=1999,
                        size=95
                        )
                    )
                ),
            dcc.Store(id='peak_distance_input_value_update', data=1),
            dcc.Store(id='peak_distance_input_value_update_acknowledged', data=2),
            dcc.Store(id='peak_distance_input_graph_update'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='peak_distance_input',
                       children=['Min Peak',html.Br(),'Distance [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('peak_distance_input_value_update_acknowledged','data'),
     Output('peak_distance_input_graph_update','data')],
    [Input('peak_distance_input','value')],
    [State('peak_distance_input_value_update','data'),
     State('peak_distance_input_value_update_acknowledged','data')])
def update_peak_distance(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'peak_distance_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]

def baseline_polynomial():
    return html.Div(id='baseline_polynomial_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'95px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='baseline_polynomial_input',
                        min=1,
                        max=25,
                        size=95
                        )
                    )
                ),
            dbc.Tooltip('degree of ploynomial function for baseline estimation',
                target='baseline_polynomial_input'),
            dcc.Store(id='baseline_polynomial_input_value_update', data=1),
            dcc.Store(id='baseline_polynomial_input_value_update_acknowledged', data=2),
            dcc.Store(id='baseline_polynomial_input_graph_update'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='baseline_polynomial_input',
                       children=['Baseline',html.Br(),'Polynomial'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('baseline_polynomial_input_value_update_acknowledged','data'),
     Output('baseline_polynomial_input_graph_update','data')],
    [Input('baseline_polynomial_input','value')],
    [State('baseline_polynomial_input_value_update','data'),
     State('baseline_polynomial_input_value_update_acknowledged','data')])
def update_baseline_polynomial(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'baseline_polynomial_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]

def baseline_switch():
    return html.Div(id='baseline_switch_container',
        className='centered_row',
        children=[
            daq.BooleanSwitch(id="baseline_switch",style={'width':'95px'}),
            html.Div(style={'width':'10px'}),
            html.Label(
                htmlFor='baseline_switch',
                children='Show Baseline',
                style={'width':'110px'}),
            dcc.Store(id='baseline_switch_on_update', data=1),
            dcc.Store(id='baseline_switch_on_update_acknowledged', data=2),
            dcc.Store(id='baseline_switch_graph_update'),]
    )
    
# if state of purge switch changes, write to config file
@app.callback(
    [Output('baseline_switch_on_update_acknowledged','data'),
     Output('baseline_switch_graph_update','data')],
    [Input('baseline_switch','on')],
    [State('baseline_switch_on_update','data'),
    State('baseline_switch_on_update_acknowledged','data')])
def activate_baseline(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'baseline_switch','attribute':'on','value':switch}])
        root.flush()
        return [no_update, time()]
    else:
        return [update, no_update]

def manual_peak_detection():
    return html.Div(id='manual_peak_detection_container',
        className='centered_row',
        children=[
            daq.BooleanSwitch(id="manual_peak_detection",style={'width':'95px'}),
            html.Div(style={'width':'10px'}),
            html.Label(
                htmlFor='manual_peak_detection',
                children='Manual Detection',
                style={'width':'110px'})
            ]
    )
    
def peak_detection_switch():
    return html.Div(id='peak_detection_switch_container',
        className='centered_row',
        children=[
            daq.BooleanSwitch(id="peak_detection_switch",style={'width':'95px'}),
            html.Div(style={'width':'10px'}),
            html.Label(
                htmlFor='peak_detection_switch',
                children='Automatic Detection',
                style={'width':'110px'}),
            dcc.Store(id='peak_detection_switch_on_update', data=1),
            dcc.Store(id='peak_detection_switch_on_update_acknowledged', data=2),
            dcc.Store(id='peak_detection_switch_graph_update'),]
    )
    
# if state of purge switch changes, write to config file
@app.callback(
    [Output('peak_detection_switch_on_update_acknowledged','data'),
     Output('peak_detection_switch_graph_update','data')],
    [Input('peak_detection_switch','on')],
    [State('peak_detection_switch_on_update','data'),
    State('peak_detection_switch_on_update_acknowledged','data')])
def activate_peak_detection(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'peak_detection_switch','attribute':'on','value':switch}])
        root.flush()
        return [no_update,time()]
    else:
        return [update,no_update]
  
# open/close collapsible section to display voltammetric parameters for displayed voltammogramm or peak detection settings
# only one of them is opened at a time and if same button is pressed again, the section is collapsed
@app.callback(
    [Output('scan_parameters_collapse','is_open'),
     Output('peak_detection_collapse','is_open'),
     Output('o2_measurement_collapse','is_open')],
    [Input('scan_parameters_button','n_clicks'),
     Input('peak_detection_button','n_clicks'),
     Input('o2_measurement_button','n_clicks')],
    [State('scan_parameters_collapse','is_open'),
     State('peak_detection_collapse','is_open'),
     State('o2_measurement_collapse','is_open')])
def open_scan_parameters(parameters_clicks,peak_clicks,o2_clicks,parameter_open,peak_open,o2_open):
    ctx = callback_context
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'scan_parameters_button':
        if parameter_open:
            return [False, False, False]
        else:
            return [True, False, False]
            
    elif trigger_id == 'peak_detection_button':
        if peak_open:
            return [False, False, False]
        else:
            return [False, True, False]
            
    elif trigger_id == 'o2_measurement_button':
        if o2_open:
            return [False, False, False]
        else:
            return [False, False, True]
    
    else:
        raise PreventUpdate

def noise_filter():
    return html.Div(id='noise_filter_container',
        className='left_row',
        children=[
            html.Button(id='noise_filter_button',
                children='Noise Filter',
                style={'width':'120px','fontSize':'xx-small','border': '1px solid #bbb','lineHeight': '20px','padding':'0 0'}),
            html.Div(style={'width':'5px'}),
            dcc.Store(id='noise_frequency_input_value_update', data=1),
            dcc.Store(id='noise_frequency_input_value_update_acknowledged', data=2),
            dcc.Input(id='noise_frequency_input',
                type='number',
                style={'backgroundColor':'transparent','color':'rgb(200, 200, 200)','width':'50px','height':'20px',
                'fontSize':'small','textAlign':'center','border': '1px solid #bbb'},
                debounce=True,
                ),
            dbc.Tooltip('typically 50Hz (Europe) or 60Hz (US), main frequency and harmonics are filtered from the data',
                target='noise_frequency_input'),
            html.Label(htmlFor='noise_frequency_input',
                children='Hz AC',
                style={'width':'70px','height':'20px','fontSize':'small','padding':'5px 5px'})
            ])

# activate/deactivate AC noise filter for linear/cyclic voltammetric measurements
@app.callback(
     Output('voltammogram_graph_file2','data'),
    [Input('noise_filter_button','n_clicks')],
    [State('voltammogram_graph_file','data')])
def set_noise_filter(n_clicks,file):
    root.flush()
    config = literal_eval(str(root.config))
    state = config['noise_filter_button']['children']
    if n_clicks != None:
        if state == 'Noise Filter Off':
            write_config([{'component':'noise_filter_button',
                       'attribute':'children','value':'Noise Filter On'}])
            return file
        else:
            write_config([{'component':'noise_filter_button',
                       'attribute':'children','value':'Noise Filter Off'}])
            return file
    else:
        raise PreventUpdate

# Set AC frequency for noise filter and trigger graph update if filter is activated
@app.callback(
    [Output('noise_frequency_input_value_update_acknowledged','data'),
     Output('voltammogram_graph_file3','data')],
    [Input('noise_frequency_input','value')],
    [State('noise_frequency_input_value_update','data'),
     State('noise_frequency_input_value_update_acknowledged','data'),
     State('voltammogram_graph_file','data')])
def update_noise_frequency(value, update, update_acknowledged, file):
    root.flush()
    config = literal_eval(str(root.config))
    state = config['noise_filter_button']['children']
    if update == update_acknowledged:
        write_config([{'component':'noise_frequency_input',
                       'attribute':'value','value':value}])
        if state == 'Noise Filter On':
            return [no_update, file]
        else:
            raise PreventUpdate
    else:
        return [update, no_update]


###########################################################
#O2 Measurement Components

def o2_lower_left():
    return html.Div(id='o2_lower_left_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'95px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='o2_lower_left_input',
                        min=-1999,
                        max=1999,
                        size=95
                        )
                    )
                ),
            dcc.Store(id='o2_lower_left_input_value_update', data=1),
            dcc.Store(id='o2_lower_left_input_value_update_acknowledged', data=2),
            dcc.Store(id='o2_lower_left_input_graph_update'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='o2_lower_left_input',
                       children=['Lower Left',html.Br(),'Limit [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('o2_lower_left_input_value_update_acknowledged','data'),
     Output('o2_lower_left_input_graph_update','data')],
    [Input('o2_lower_left_input','value')],
    [State('o2_lower_left_input_value_update','data'),
     State('o2_lower_left_input_value_update_acknowledged','data')])
def update_o2_lower_left(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'o2_lower_left_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]
        
        
def o2_lower_right():
    return html.Div(id='o2_lower_right_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'95px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='o2_lower_right_input',
                        min=-1999,
                        max=1999,
                        size=95
                        )
                    )
                ),
            dcc.Store(id='o2_lower_right_input_value_update', data=1),
            dcc.Store(id='o2_lower_right_input_value_update_acknowledged', data=2),
            dcc.Store(id='o2_lower_right_input_graph_update'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='o2_lower_right_input',
                       children=['Lower Right',html.Br(),'Limit [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('o2_lower_right_input_value_update_acknowledged','data'),
     Output('o2_lower_right_input_graph_update','data')],
    [Input('o2_lower_right_input','value')],
    [State('o2_lower_right_input_value_update','data'),
     State('o2_lower_right_input_value_update_acknowledged','data')])
def update_o2_lower_right(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'o2_lower_right_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]
        
def o2_upper_left():
    return html.Div(id='o2_upper_left_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'95px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='o2_upper_left_input',
                        min=-1999,
                        max=1999,
                        size=95
                        )
                    )
                ),
            dcc.Store(id='o2_upper_left_input_value_update', data=1),
            dcc.Store(id='o2_upper_left_input_value_update_acknowledged', data=2),
            dcc.Store(id='o2_upper_left_input_graph_update'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='o2_upper_left_input',
                       children=['Upper Left',html.Br(),'Limit [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('o2_upper_left_input_value_update_acknowledged','data'),
     Output('o2_upper_left_input_graph_update','data')],
    [Input('o2_upper_left_input','value')],
    [State('o2_upper_left_input_value_update','data'),
     State('o2_upper_left_input_value_update_acknowledged','data')])
def update_o2_upper_left(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'o2_upper_left_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]
        
        
def o2_upper_right():
    return html.Div(id='o2_upper_right_input_container',
        className='centered_row',
        children=[
            html.Div(
                style={'width':'95px'},
                children=daq.DarkThemeProvider(
                    theme=light_theme,
                    children=daq.NumericInput(
                        id='o2_upper_right_input',
                        min=-1999,
                        max=1999,
                        size=95
                        )
                    )
                ),
            dcc.Store(id='o2_upper_right_input_value_update', data=1),
            dcc.Store(id='o2_upper_right_input_value_update_acknowledged', data=2),
            dcc.Store(id='o2_upper_right_input_graph_update'),
            html.Div(style={'width':'10px'}),
            html.Label(htmlFor='o2_upper_right_input',
                       children=['Upper Right',html.Br(),'Limit [mV]'],
                       style={'width':'110px'}
                       ),
            ]
        )
@app.callback(
    [Output('o2_upper_right_input_value_update_acknowledged','data'),
     Output('o2_upper_right_input_graph_update','data')],
    [Input('o2_upper_right_input','value')],
    [State('o2_upper_right_input_value_update','data'),
     State('o2_upper_right_input_value_update_acknowledged','data')])
def update_o2_upper_right(value, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'o2_upper_right_input',
                       'attribute':'value','value':value}])
        return [no_update, time()]
    else:
        return [update, no_update]
        
def o2_measurement_switch():
    return html.Div(id='o2_measurement_switch_container',
        className='centered_row',
        children=[
            daq.BooleanSwitch(id="o2_measurement_switch",style={'width':'95px'}),
            html.Div(style={'width':'10px'}),
            html.Label(
                htmlFor='o2_measurement_switch',
                children='Measure O2',
                style={'width':'110px'}),
            dcc.Store(id='o2_measurement_switch_on_update', data=1),
            dcc.Store(id='o2_measurement_switch_on_update_acknowledged', data=2),
            dcc.Store(id='o2_measurement_switch_graph_update'),]
    )
    
# if state of purge switch changes, write to config file
@app.callback(
    [Output('o2_measurement_switch_on_update_acknowledged','data'),
     Output('o2_measurement_switch_graph_update','data')],
    [Input('o2_measurement_switch','on')],
    [State('o2_measurement_switch_on_update','data'),
    State('o2_measurement_switch_on_update_acknowledged','data')])
def activate_o2_measurement(switch, update, update_acknowledged):
    if update == update_acknowledged:
        write_config([{'component':'o2_measurement_switch','attribute':'on','value':switch}])
        root.flush()
        return [no_update, time()]
    else:
        return [update, no_update]