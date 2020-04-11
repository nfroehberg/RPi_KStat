# GUI Frontend for the KStat electrochemical analyzer
# Main Script to initialize the interface and main structure of the program
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
import json
import kstat_interface.dash_apps.hg_plater as hg_plater
import kstat_interface.dash_apps.single_CV as single_CV
import kstat_interface.dash_apps.single_DPV as single_DPV
import kstat_interface.dash_apps.electrode_test as electrode_test
from kstat_interface.dash_apps.app import app
from kstat_interface import redis_config
from subprocess import call
import pathlib
import os, shutil
# to add a component that communicates with the backend:
#
# add component plus two dcc.Store components with data=1 and data=2
# the store components are used to differentiate human input from changes made by the backend
# the initial value is thus interpreted as a backend change to prevent it being written to the config
#
# add the component to the update_config function with the appropriate
# output and state callback identifiers as well as adding the checks for updates
# of the particular attributes
#
# add callback function with the states of both store components
# if the store components differ, the callback was triggered by a backend update
# so no action should happen. in this case update the second store component to
# equal the first to acknowledge the update

def initialize_redis():
    redis_host,redis_port = redis_config.get_config()
    global root
    root = Root(host=redis_host, port=redis_port, db=0)

def get_program():
    program=str(root.program)
    if program == 'startup':
        program = None
    return program
    
def clearDirectory(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

dark_theme={
    'dark': True,
    'detail': '#007439',
    'primary': '#8be3ff',
    'secondary': '#6E6E6E',
}
def setup_layout():
    return html.Div(
            style = {'height':'100%','width':'100%'},
            children=[
                html.H1('KStat Control Center',style = {'width':'100%'}),
                dcc.Dropdown(
                    id='program_dropdown',
                    clearable=False,
                    options=[
                        {'value':'hg_plater','label':'Hg Electrode Plating'},
                        {'value':'electrode_test','label':'Electrode Test'},
                        {'value':'single_CV','label':'Single Measurement - Cyclic Voltammetry'},
                        {'value':'single_DPV','label':'Single Measurement - Differential Pulse Voltammetry'}
                        ],
                    placeholder='Select a program',
                    value=get_program(),
                    className='program_dropdown'
                    ),
                daq.DarkThemeProvider(
                    theme=dark_theme,
                    children=html.Div(
                        style={'width':'100%','display':'flex','justifyContent':'center','alignItems':'center'},
                        children=html.Div(id='main_program',className='main_program'))),
                html.Footer(
                    style={'position':'fixed','bottom':'0%','left':'0%'},
                    children=daq.DarkThemeProvider(
                        theme=dark_theme,
                        children=html.Div(
                            className='left_row',
                            children=[
                                daq.PowerButton(
                                    color='red',on=True,
                                    style={'height':'75px'},
                                    label='Power Off',
                                    id='power_button'),
                                html.Div(style={'width':'10px'}),
                                daq.PowerButton(
                                    color='yellow',on=True,
                                    style={'height':'75px'},
                                    label='Reboot',
                                    id='reboot_button')])))
                    ])

# Load Program based on dropdown selection
programs = {'hg_plater':hg_plater.main(), 'single_CV':single_CV.main(),
            'single_DPV':single_DPV.main(),'electrode_test':electrode_test.main()}
@app.callback(
    Output('main_program','children'),
    [Input('program_dropdown','value')])
def setprogram(program):
    if program != None:
        root.program = program
        return programs[program]
    else:
        return no_update

# Shut down the RPi
@app.callback(
    Output('power_button','color'),
    [Input('power_button','on')])
def power_off(on):
    if not on:
        call("sudo shutdown -h now", shell=True)
        return no_update
    else:
        raise PreventUpdate

#Reboot the RPi
@app.callback(
    Output('reboot_button','color'),
    [Input('reboot_button','on')])
def power_off(on):
    if not on:
        print('reboot')
        call("sudo reboot", shell=True)
        return no_update
    else:
        raise PreventUpdate

if __name__ == '__main__':
    while True:
        try:
            initialize_redis()
            try:
                program=root.program
            except:
                root.program = 'startup'
                
            main_directory = str(pathlib.Path(__file__).parent.absolute())
            root.main_directory = main_directory + '/'
            root.data_directory = main_directory + '/data/'
            root.download_directory = main_directory + '/user_downloads/'
            clearDirectory(str(root.download_directory)) # empty user download directory on reboot to prevent memory filling up
            root.working_directory = root.data_directory

            app.layout = setup_layout()
            app.run_server(debug=False, host='10.3.141.1', port=8080)
        except Exception as e:
            print(e)
            sleep(1)
