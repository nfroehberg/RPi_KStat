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
from numpy import mean, abs
import pandas as pd
import peakutils as pu

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

def plot_scan():
    return html.Div(id='voltammogram_graph_container',
        style={'width':'100%'},
        children=[
            dcc.Store(id='voltammogram_graph_file'),
            dcc.Store(id='voltammogram_graph_file2'),
            dcc.Store(id='voltammogram_graph_file3'),
            dcc.Store(id='voltammogram_graph_file4'),
            dcc.Store(id='voltammogram_graph_file5'),
            dcc.Graph(id='voltammogram_graph'),
            dcc.Store(id='voltammogram_point1',data='no point'),
            dcc.Store(id='voltammogram_point2',data='no point'),
            dcc.Store(id='clear_points'),
            ]
        )
        
@app.callback(
    [Output('voltammogram_graph','figure'),
     Output('scan_parameters_collapse','children'),
     Output('noise_filter_container','style'),
     Output('peak_file_data','data')],
    [Input('voltammogram_graph_file','data'),
     Input('voltammogram_graph_file2','data'),
     Input('voltammogram_graph_file3','data'),
     Input('voltammogram_graph_file4','data'),
     Input('voltammogram_graph_file5','data')],
     [State('voltammogram_point1','data'),
      State('voltammogram_point2','data')])
def update_plot_scan(file,file2,file3,file4,file5,point1,point2):
    ctx = dash.callback_context
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'voltammogram_graph_file2': # triggered by noise filter button
        file = file2
    elif trigger_id == 'voltammogram_graph_file3': # triggered by noise frequency update
        file = file3
    elif trigger_id == 'voltammogram_graph_file4': # triggered by peak detection update
        file = file4
    elif trigger_id == 'voltammogram_graph_file5': # triggered by click on plot
        file = file5
    
    params = get_parameters(file)
    collapse_params = generate_param_components(params)
    df = pd.read_csv(file)
    root.flush()
    config = literal_eval(str(root.config))
    graph_title = file.replace(str(root.working_directory),'').replace('.csv','')
    
    x_data = df.potential
    plot_data=[{'x':x_data,'marker':{'color':'rgb(155,240,255)'},'name':'current'}]
    
    noise_filter_button = config['noise_filter_button']['children']
    noise_frequency = config['noise_frequency_input']['value']
    if params['type']['value'] in ['Cyclic Voltammetry','Linear Sweep Voltammetry']:
        y_data = df.current
        plot_data[0]['y'] = y_data
        noise_filter = {'display':'flex','alignItems':'center'}
        if noise_filter_button == 'Noise Filter On':
            data_label = 'current_filtered_{}Hz'.format(noise_frequency)
            if data_label in df.columns:
                y_data = df[data_label]
                plot_data[0]['y'] = y_data
            else:
                y_data = ac_noise_filter(noise_frequency,params['Samplerate']['value'],df.current)
                plot_data[0]['y'] = y_data
                df[data_label] = y_data
                df.to_csv(file, index=False)
    elif params['type']['value'] in ['Differential Pulse Voltammetry','Squarewave Voltammetry']:
        y_data = df.fbcurrent
        plot_data[0]['y'] = y_data
        noise_filter = {'display':'none'}
    
    if not config['peak_detection_switch']['on'] and point1 == 'no point':
        peakfile = ''
    else:
        peakfile = [file.replace('.csv','-peaks.txt')]
        peakfile.append('ID,Detection Mode,Peak Potential [mV],Peak Current [A],\n')
    
    if config['peak_detection_switch']['on']:
        baseline_polynomial = config['baseline_polynomial_input']['value']
        peak_threshold = config['peak_threshold_input']['value']/config['peak_threshold_range']['value']
        mv_step = (x_data.iloc[0]-x_data.iloc[9])/10
        peak_dist = int(config['peak_distance_input']['value']/mv_step)
        peak_width = int(config['peak_width_input']['value']/mv_step)
        
        # positive or negative current
        if mean(y_data) < 0:
            scale_factor = -1
        else:
            scale_factor = 1
            
        base = pu.baseline(y_data*scale_factor, baseline_polynomial)
        peaks = pu.peak.indexes(y_data*scale_factor-base, thres=peak_threshold, min_dist=peak_dist, thres_abs=True)
        peaks_gaussian = pu.peak.interpolate(x_data.values, (y_data*scale_factor-base).values, ind=peaks, width=peak_width)
        peaks_gaussian_indices = []
        for peak in peaks_gaussian:
            peaks_gaussian_indices.append((abs(x_data.values - peak)).argmin())
        peaks_x = x_data.iloc[peaks_gaussian_indices]
        peaks_y = y_data.iloc[peaks_gaussian_indices]
        y_base_removed = y_data*scale_factor-base
        peak_heights = y_base_removed.iloc[peaks_gaussian_indices]
        peaks_labels = []
        for i in range(len(peaks_x)):
            peaks_labels.append('{0:.0f} mV<br>{1:.2E} A'.format(peaks_x.iloc[i],peak_heights.iloc[i]))
            peakfile[1] = peakfile[1] + '{},automatic,{:.0f},{:.2E},\n'.format(graph_title,peaks_x.iloc[i],peak_heights.iloc[i])
        plot_data.append({'x':peaks_x,'y':peaks_y,
                          'mode':'markers+text',
                          'marker':{'color':'rgb(255,120,0)'},
                          'text':peaks_labels,
                          'textfont':{'color':'rgb(255,255,255)'},
                          'textposition':'top center',
                          'name':'peak'})
        if config['baseline_switch']['on']:
            plot_data.append({'x':x_data,'y':base*scale_factor,
                              'marker':{'color':'rgb(0,180,0)'},
                              'name':'baseline'})
    
    # manual click points
    if point1 != 'no point':
        points = [point1]
        if point2 != 'no point':
            points.append(point2)
        x_points = x_data.iloc[points]
        y_points = y_data.iloc[points]
        plot_data.append({'x':x_points,'y':y_points,
                          'mode':'markers+text',
                          'marker':{'color':'rgb(255,0,0)'},
                          'name':'click'})
        if point2 != 'no point':
            # lines to connect points and show horizontal and vertical distance
            v_diff = abs(x_points.iloc[0]-x_points.iloc[1])
            i_diff = abs(y_points.iloc[0]-y_points.iloc[1])
            plot_data.append({'x':[x_points.iloc[0],x_points.iloc[1],x_points.iloc[1]],
                              'y':[y_points.iloc[0],y_points.iloc[0],y_points.iloc[1]],
                              'mode':'lines','marker':{'color':'rgb(255,0,0)'}})
            plot_data.append({'x':[x_points.iloc[0]+((x_points.iloc[1]-x_points.iloc[0])/2),x_points.iloc[1]],
                              'y':[y_points.iloc[0],y_points.iloc[0]+((y_points.iloc[1]-y_points.iloc[0])/2)],
                              'text':['{:.0f} mV'.format(v_diff),'{:.2E} A'.format(i_diff)],
                              'mode':'text','textfont':{'color':'rgb(255,0,0)'},
                              'textposition':['bottom center','middle right'],})
            peakfile[1] = peakfile[1] + '{},manual,{:.0f},{:.2E},\n'.format(graph_title,x_points.iloc[1],i_diff)
    
    figure={
        'data':plot_data,
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
            'plot_bgcolor':'rgba(0,0,0,0)',
            'showlegend':False,
            }
        }
    return [figure,collapse_params,noise_filter,peakfile]

# if points on graph are clicked, get index. if already two points are selected, remove all
# if graph file is changed, clear points
@app.callback(
    [Output('voltammogram_point1','data'),
     Output('voltammogram_point2','data'),
     Output('voltammogram_graph_file5','data')],
    [Input('voltammogram_graph','clickData'),
     Input('clear_points','data')],
    [State('voltammogram_point1','data'),
     State('voltammogram_point2','data'),
     State('voltammogram_graph_file','data'),
     State('manual_peak_detection','on')])
def catch_click(clickData,clear_points,point1,point2,file,switch):
    ctx = dash.callback_context
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'clear_points':
        return ['no point', 'no point', file]
    elif clickData != None and switch:
        index = clickData['points'][0]['pointIndex']
        if point1 == 'no point':
            return [index, no_update, file]
        elif point2 == 'no point':
            return [no_update, index, file]
        else:
            return ['no point', 'no point', file]
    else:
        raise PreventUpdate

# generate dash components to display scan parameters
def generate_param_components(params):
    param_components = []
    for factor in params:
        label = html.Div(children=params[factor]['label'], style={'width':'180px'})
        value = html.Div(children=params[factor]['value'], style={'width':'250px'})
        param_components.append(html.Div(children=[label,value],className='centered_row'))
    return html.Div(children=param_components,className='left_row')


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
    
    return pd.Series(yf5)

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