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
import kstat_interface.dash_apps.main_app as main_app
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

initial_config={
    'purge_switch':{'on':False,'disabled':False},
    'stirr_switch':{'on':False,'disabled':False},
    'scan_progress':{'value':0},
    'scan_progress_label':{'children':''},
    'series_progress':{'value':70},
    'series_progress_label':{'children':''},
    'stirr_speed_slider':{'value':1000},
    'cleaning_potential_input':{'value':-900},
    'deposition_potential_input':{'value':-100},
    'cleaning_time_input':{'value':5},
    'deposition_time_input':{'value':2},
    'purge_time_input':{'value':60},
    'start_potential_input':{'value':-100},
    'vertex_potential_input':{'value':-1850},
    'end_potential_input':{'value':-100},
    'slope_input':{'value':500},
    'pulse_height_input':{'value':50},
    'samplefreq_input':{'value':'1KHz'},
    'iv_gain_input':{'value':'POT_GAIN_300K'},
    'pga_gain_input':{'value':2},
    'n_scans_input':{'value':1},
    'step_size_input':{'value':4},
    'period_input':{'value':300},
    'pulse_width_input':{'value':40},
    'frequency_input':{'value':50},
    'category_selection':{'value':'voltammetry_single'},
    'program_selection':{'value':'single_cv','options':[]},
    'plating_potential_input':{'value':-100},
    'plating_time_input':{'value':180},
    'comment_input':{'value':''},
    'n_electrode_tests_input':{'value':20},
    'start_button':{'disabled':False,'triggered':False},
    'stop_button':{'disabled':True,'triggered':False},
    'popup_measurement_id':{'value':''},
    'upload_button':{'disabled':False},
    'download_button':{'disabled':False},
    'change_directory_button':{'disabled':False},
    'noise_filter_button':{'children':'Noise Filter On'},
    'noise_frequency_input':{'value':50},
    'peak_detection_switch':{'on':False},
    'baseline_switch':{'on':False},
    'peak_threshold_input':{'value':300},
    'peak_threshold_range':{'value':1000000000000},
    'peak_distance_input':{'value':100},
    'baseline_polynomial_input':{'value':4},
    'peak_width_input':{'value':20},
    'scan_selector':{'options':[],'value':''},
    }

def initialize_config(root):
    for component in initial_config.keys():
        try:
            root_config_component = root.config[component]
            for parameter in initial_config[component].keys():
                try:
                    root_config_component_parameter = root.config[component][parameter]
                except:
                    config=literal_eval(str(root.config))
                    config[component][parameter] = initial_config[component][parameter]
                    root.config=config
                    print('initializing', component, parameter)
        except:
            config=literal_eval(str(root.config))
            config[component]=initial_config[component]
            root.config=config
            print('initializing', component)
    root.flush()
    
def setup_layout():
    return html.Div(
            style = {'height':'100%','width':'100%'},
            children=[
                daq.DarkThemeProvider(
                    theme=dark_theme,
                    children=html.Div(
                        style={'width':'100%','display':'flex','justifyContent':'center','alignItems':'center'},
                        children=main_app.main())),
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
            root.program='measurement'
            initialize_config(root)

            app.layout = setup_layout()
            app.run_server(debug=False, host='voltammetrypi.local', port=8080)
        except Exception as e:
            print(e)
            sleep(1)
