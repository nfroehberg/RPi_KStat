# GUI Frontend for the KStat electrochemical analyzer
# This script provides plotly graphs of voltammetric scans
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
from scipy import signal
import pandas as pd

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

def plot_scan():
    return html.Div(id='voltammogram_graph_container',
        style={'width':'100%'},
        children=[
            dcc.Store(id='voltammogram_graph_file'),
            dcc.Store(id='voltammogram_graph_file2'),
            dcc.Store(id='voltammogram_graph_file3'),
            dcc.Graph(id='voltammogram_graph'),
            ]
        )

# generate dash components to display scan parameters
def generate_param_components(params):
    param_components = []
    for factor in params:
        label = html.Div(children=params[factor]['label'], style={'width':'180px'})
        value = html.Div(children=params[factor]['value'], style={'width':'250px'})
        param_components.append(html.Div(children=[label,value],className='centered_row'))
    return html.Div(children=param_components,className='left_row')

@app.callback(
    [Output('voltammogram_graph','figure'),
     Output('scan_parameters_collapse','children'),
     Output('noise_filter_container','style')],
    [Input('voltammogram_graph_file','data'),
     Input('voltammogram_graph_file2','data'),
     Input('voltammogram_graph_file3','data')])
def update_plot_scan(file,file2,file3):
    ctx = dash.callback_context
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'voltammogram_graph_file2': # triggered by noise filter button
        file = file2
    elif trigger_id == 'voltammogram_graph_file3': # triggered by noise frequency update
        file = file3
    
    params = get_parameters(file)
    collapse_params = generate_param_components(params)
    df = pd.read_csv(file)
    root.flush()
    config = literal_eval(str(root.config))
    graph_title = file.replace(str(root.working_directory),'').replace('.csv','')
    
    noise_filter_button = config['noise_filter_button']['children']
    noise_frequency = config['noise_frequency_input']['value']
    if params['type']['value'] in ['Cyclic Voltammetry','Linear Sweep Voltammetry']:
        y_data = df.current
        noise_filter = {'display':'flex','alignItems':'center'}
        if noise_filter_button == 'Noise Filter On':
            data_label = 'current_filtered_{}Hz'.format(noise_frequency)
            if data_label in df.columns:
                y_data = df[data_label]
            else:
                y_data = ac_noise_filter(noise_frequency,params['Samplerate']['value'],df.current)
                df[data_label] = y_data
                df.to_csv(file, index=False)
    elif params['type']['value'] in ['Differential Pulse Voltammetry','Squarewave Voltammetry']:
        y_data = df.fbcurrent
        noise_filter = {'display':'none'}
        
    x_data = df.potential 
    
    figure={
        'data':[{'x':x_data,
                 'y':y_data,
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
    return [figure,collapse_params,noise_filter]
    
# remove AC noise (fixed frequency) from linear and cyclic voltammetric data
# Filter: IIR notch
Samplingrates = {"2.5Hz":2.5, "5Hz":5.0, "10Hz":10.0, "15Hz":15.0,
                 "25Hz":25.0, "30Hz":30.0, "50Hz":50.0, "60Hz":60.0,
                 "100Hz":100.0, "500Hz":500.0, "1KHz":1000.0, "2KHz":2000.0,
                 "3.75KHz":3750.0, "7.5KHz":7500.0, "15KHz":1500.0, "30KHz":30000.0}

def ac_noise_filter(noise_freq, sample_freq, data):
    # constructing IIR notch filters
    fs = Samplingrates[sample_freq]   # Sample frequency (Hz)
    f0 = noise_freq  # Frequency to be removed from signal (Hz)
    Q = 2.0  # Quality factor
    
    # Design notch filter for base frequency and harmonics
    b, a = signal.iirnotch(f0, Q, fs)
    c, d = signal.iirnotch(f0*2, Q, fs)
    e, f = signal.iirnotch(f0*4, Q, fs)
    g, h = signal.iirnotch(f0*5, Q, fs)
    i, j = signal.iirnotch(f0*6, Q, fs)
    
    #apply filters
    yf1 = signal.filtfilt(b,a,data)
    yf2 = signal.filtfilt(c,d,yf1) 
    yf3 = signal.filtfilt(e,f,yf2) 
    yf4 = signal.filtfilt(g,h,yf3) 
    yf5 = signal.filtfilt(i,j,yf4)
    
    return yf5

factors={'Cyclic Voltammetry Experiment\n':
    ['Comment','Samplerate','t_preconditioning1','t_preconditioning2',
    'v_preconditioning1','v_preconditioning2',
    'v1','v2','start','n_scans','slope'],
    'Linear Sweep Voltammetry Experiment\n':
    ['Comment','Samplerate','t_preconditioning1','t_preconditioning2',
    'v_preconditioning1','v_preconditioning2','start','stop','slope'],
    'Differential Pulse Voltammetry Experiment\n':
    ['Comment','Samplerate','t_preconditioning1','t_preconditioning2',
    'v_preconditioning1','v_preconditioning2','start','stop',
    'step_size','pulse_height','period','width'],
    'Squarewave Voltammetry Experiment\n':
    ['Comment','Samplerate','t_preconditioning1','t_preconditioning2',
    'v_preconditioning1','v_preconditioning2','start','stop',
    'step_size','pulse_height','frequency','n_scans']}
labels={'Comment':'Comment','Samplerate':'Sampling Frequency','t_preconditioning1':'Cleaning Time',
    't_preconditioning2':'Deposition Time','v_preconditioning1':'Cleaning Potential',
    'v_preconditioning2':'Deposition Potential','v1':'Vertex Potential','v2':'End Potential',
    'start':'Start Potential','stop':'End Potential','n_scans':'Number of Scans','slope':'Slope',
    'step_size':'Step Size','pulse_height':'Pulse Height','period':'Period',
    'width':'Pulse Width','frequency':'Frequency'}
experiment_types={'Cyclic Voltammetry Experiment\n':'Cyclic Voltammetry',
                  'Linear Sweep Voltammetry Experiment\n':'Linear Sweep Voltammetry',
                  'Squarewave Voltammetry Experiment\n':'Squarewave Voltammetry',
                  'Differential Pulse Voltammetry Experiment\n':'Differential Pulse Voltammetry'}
                  
# read scan parameters from the .txt file generated by the KStat driver
def get_parameters(file):
    # get parameter data
    parafile = file.replace('.csv','-parameters.txt')
    f = open(parafile,'r')
    type = f.readline()
    f.close()
    parameters = pd.read_csv(parafile, delim_whitespace=True, engine='python', names=['0','1','2','3'], index_col=0)
    params = {}
    params['type'] = {'label':'Type','value':experiment_types[type]}
    for factor in factors[type]:
        number = parameters['2'][factor]
        unit = parameters['3'][factor]
        if unit != None:
            value = number + ' ' + unit
        else:
            value = number
        params[factor] = {'label':labels[factor],'value':value}
    return params