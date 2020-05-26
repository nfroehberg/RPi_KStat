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
from dash import no_update
from redisworks import Root
from .. import redis_config
from .app import app, write_config
from ast import literal_eval

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
            html.Div(className='left_row',
                children=[
                    html.Button(children='Scan Parameters',
                        id='scan_parameters_button',
                        style={'width':'250px','fontSize':'xx-small','border': '1px solid #bbb','lineHeight': '20px'}),
                    html.Div(id='noise_filter_container',
                        children=[
                            html.Div(style={'width':'5px'}),
                            html.Button(id='noise_filter_button',
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
                            html.Label(htmlFor='noise_frequency_input',
                                children='Hz AC',
                                style={'width':'70px','height':'20px','fontSize':'small','padding':'5px 5px'})
                            ])
                    ]),
            dbc.Collapse(id='scan_parameters_collapse',
                children='Hello')])

# open/close collapsible section to display voltammetric parameters for displayed voltammogramm
@app.callback(
    Output('scan_parameters_collapse','is_open'),
    [Input('scan_parameters_button','n_clicks')],
    [State('scan_parameters_collapse','is_open')])
def open_scan_parameters(n_clicks,is_open):
    if n_clicks != None:
        if is_open:
            return False
        else:
            return True
    else:
        raise PreventUpdate

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