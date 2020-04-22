# GUI Frontend for the KStat electrochemical analyzer
# start and stop buttons for all programs and the associated confirmation popups
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

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

# component for start button and measurement id popup
def start():
    return html.Div(id='start_button_container',
        style={'width':'40%'},
        children=[
            html.Button(id='start_button',
                children='Start',
                style={'width':'90%'}),
            dcc.Store(id='start_button_popup_placeholder1'),
            dcc.Store(id='start_button_popup_placeholder2'),
            dcc.Store(id='start_button_popup_placeholder3'),
            dbc.Modal(id='start_button_popup',
                centered=True,
                children=[
                    dbc.ModalHeader(),
                    dbc.ModalBody(
                        children=html.Div(
                            className='centered_row',
                            children=[
                                dcc.Input(id='popup_measurement_id',
                                    debounce=True,
                                    type='text',
                                    placeholder='Measurement ID'),
                                html.Div(style={'width':'15px'}),
                                html.Button(id='popup_start_button',
                                    children='Go!',),
                                html.Div(style={'width':'15px'}),
                                html.Button(id='popup_cancel_button',
                                    children='Cancel'),
                                ]
                            )
                        ),
                    dbc.ModalFooter()
                    ]
                )
            ]
        )

# get measurement id and send trigger signal to start measurement
@app.callback(
    Output('start_button_popup_placeholder3','data'),
    [Input('popup_start_button','n_clicks')],
    [State('popup_measurement_id','value')])
def startMeasurement(n_clicks,id2):
    if n_clicks != None and id2 != None and id2 != '':
        write_config([{'component':'start_button','attribute':'triggered','value':True},
                        {'component':'popup_measurement_id','attribute':'value','value':id2},
                        {'component':'stop_button','attribute':'disabled','value':False},
                        {'component':'start_button','attribute':'disabled','value':True}])
        return 'close'
    else:
        raise PreventUpdate

# close starting popup when cancel button is clicked
@app.callback(
    Output('start_button_popup_placeholder2','data'),
    [Input('popup_cancel_button','n_clicks')])
def cancelStartPopup(n_clicks):
    if n_clicks != None:
        return 'close'
    else:
        raise PreventUpdate

# start electrode plating or open popup to get measurement id
@app.callback(
    Output('start_button_popup_placeholder1','data'),
    [Input('start_button','n_clicks')],
    [State('program_selection','value')])
def openStartPopup(n_clicks,program):
    if n_clicks != None:
        if program == 'hg_au_electrode_plating':
            write_config([{'component':'start_button','attribute':'triggered','value':True},
                            {'component':'stop_button','attribute':'disabled','value':False},
                            {'component':'start_button','attribute':'disabled','value':True}])
            raise PreventUpdate
        else:
            return 'open'
    else:
        raise PreventUpdate
   
# since the modal popup is opened by one button and closed by another,
# two placeholder components are used to control its open state
@app.callback(
    Output('start_button_popup','is_open'),
    [Input('start_button_popup_placeholder1','data'),
     Input('start_button_popup_placeholder2','data'),
     Input('start_button_popup_placeholder3','data')])
def open_close_start_popup(placeholder1,placeholder2,placeholder3):
    #determining which input was triggered to determine whether to open or close the modal
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if trigger_id == 'start_button_popup_placeholder1':
        return True
    elif trigger_id == 'start_button_popup_placeholder2':
        return False
    elif trigger_id == 'start_button_popup_placeholder3':
        return False
    else:
        return False



# component for stop button to cancel measurements
def stop():
    return html.Div(id='stop_button_container',
        style={'width':'40%'},
        children=[
            html.Button(id='stop_button',
                children='Stop',
                style={'width':'90%'},
                disabled=True),
            dcc.ConfirmDialog(id='stop_measurement_confirmation',
                message='Stop Measurement?'),
            dcc.Store(id='stop_measurement_confirmation_placeholder'),
            ]
        )
   
# open confirmation dialog when stop button is clicked
@app.callback(
    Output('stop_measurement_confirmation','displayed'),
    [Input('stop_button','n_clicks')])
def cancelMeasurementConfirmation(n_clicks):
    if n_clicks != None:
        return True
    else:
        raise PreventUpdate
# after confirmation, cancel measurement
@app.callback(
    Output('stop_measurement_confirmation_placeholder','data'),
    [Input('stop_measurement_confirmation','submit_n_clicks')])
def cancelMeasurement(n_clicks):
    if n_clicks != None:
        write_config([{'component':'stop_button','attribute':'triggered','value':True},
                        {'component':'stop_button','attribute':'disabled','value':True},
                        {'component':'start_button','attribute':'disabled','value':False},])
    raise PreventUpdate 