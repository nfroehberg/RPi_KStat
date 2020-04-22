# GUI Frontend for the KStat electrochemical analyzer
# Dropdown selection of category and program for measurements etc.
# controls program selection for backend and visibility of input components etc.
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
from .app import app, write_config
from .. import redis_config
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

visibility_controlled_components =[
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'vertex_potential_input_container',
    'end_potential_input_container',
    'slope_input_container',
    'pulse_height_input_container',
    'step_size_input_container',
    'period_input_container',
    'pulse_width_input_container',
    'frequency_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'n_scans_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'series_progress_container',
    'file_management',
    'plating_time_input_container',
    'plating_potential_input_container',
    'comment_input_container',
    'n_electrode_tests_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
single_cv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'vertex_potential_input_container',
    'end_potential_input_container',
    'slope_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'n_scans_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
single_lv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'end_potential_input_container',
    'slope_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'n_scans_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
single_dpv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'end_potential_input_container',
    'step_size_input_container',
    'pulse_height_input_container',
    'pulse_width_input_container',
    'period_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
single_swv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'end_potential_input_container',
    'step_size_input_container',
    'pulse_height_input_container',
    'frequency_input_container',
    'samplefreq_input_container',
    'n_scans_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
standard_addition_cv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'vertex_potential_input_container',
    'end_potential_input_container',
    'slope_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'n_scans_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'series_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
standard_addition_lv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'end_potential_input_container',
    'slope_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'n_scans_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'series_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
standard_addition_dpv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'end_potential_input_container',
    'step_size_input_container',
    'pulse_height_input_container',
    'pulse_width_input_container',
    'period_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'series_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
standard_addition_swv_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'end_potential_input_container',
    'step_size_input_container',
    'pulse_height_input_container',
    'frequency_input_container',
    'samplefreq_input_container',
    'n_scans_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'series_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    ]
    
hg_au_electrode_testing_components = [
    'cleaning_potential_input_container',
    'deposition_potential_input_container',
    'cleaning_time_input_container',
    'deposition_time_input_container',
    'purge_time_input_container',
    'start_potential_input_container',
    'vertex_potential_input_container',
    'end_potential_input_container',
    'slope_input_container',
    'samplefreq_input_container',
    'iv_gain_input_container',
    'pga_gain_input_container',
    'n_scans_input_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'series_progress_container',
    'file_management',
    'n_electrode_tests_input_container',
    'start_button_container',
    'stop_button_container',
    ]

hg_au_electrode_plating_components = [
    'plating_potential_input_container',
    'plating_time_input_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'start_button_container',
    'stop_button_container',
    ]

def category_selection():
    return html.Div(id='category_selection_container',
        style={'width':'30%'},
        children=[
            dcc.Store(id='category_selection_value_update', data=1),
            dcc.Store(id='category_selection_value_update_acknowledged', data=2),
            dcc.Dropdown(
                id='category_selection',
                style={'color':'black'},
                clearable=False,
                options=[
                    {'label':'Voltammetry - Single Measurement','value':'voltammetry_single'},
                    {'label':'Voltammetry - Standard Addition','value':'voltammetry_standard_addition'},
                    {'label':'Hg/Au Electrode Fabrication','value':'hg_au_electrode_fabrication'},
                    ]
                ),
            ]
        )
@app.callback(
    Output('category_selection_value_update_acknowledged','data'),
    [Input('category_selection','value')],
    [State('category_selection_value_update','data'),
     State('category_selection_value_update_acknowledged','data')])
def update_category(value, update, update_acknowledged):
    if update == update_acknowledged:
        
        write_config([{'component':'category_selection',
                       'attribute':'value','value':value}])
                       
        if value == 'voltammetry_single':
            options = [
                {'label':'Cyclic','value':'single_cv'},
                {'label':'Linear','value':'single_lv'},
                {'label':'Differential Pulse','value':'single_dpv'},
                {'label':'Squarewave','value':'single_swv'},]
        elif value == 'voltammetry_standard_addition':
            options = [
                {'label':'Cyclic','value':'standard_addition_cv'},
                {'label':'Linear','value':'standard_addition_lv'},
                {'label':'Differential Pulse','value':'standard_addition_dpv'},
                {'label':'Squarewave','value':'standard_addition_swv'},]
        elif value == 'hg_au_electrode_fabrication':
            options = [
                {'label':'Mercury Plating','value':'hg_au_electrode_plating'},
                {'label':'Electrode Testing','value':'hg_au_electrode_testing'}]
        else:
            options = []
        
        write_config([{'component':'program_selection',
                       'attribute':'options','value':options}])
        return no_update
    else:
        return update


    
def program_selection():
    return html.Div(id='program_selection_container',
        style={'width':'30%'},
        children=[
            dcc.Store(id='program_selection_value_update', data=1),
            dcc.Store(id='program_selection_value_update_acknowledged', data=2),
            dcc.Store(id='program_selection_value_first_update', data=1),
            dcc.Dropdown(
                id='program_selection',
                style={'color':'black'},
                clearable=False,
                ),
            ]
        )
   
visibility_outputs=[
    Output('program_selection_value_update_acknowledged','data'),
    Output('program_selection_value_first_update','data'),]
visibility_states=[
    State('program_selection_value_update','data'),
    State('program_selection_value_update_acknowledged','data'),
    State('program_selection_value_first_update','data'),]
for component in visibility_controlled_components:
    visibility_outputs.append(Output(component,'style'))
    visibility_states.append(State(component,'style'))
visibility_controlled_components_labels=visibility_controlled_components

component_lists={
    'single_cv':single_cv_components,
    'single_lv':single_lv_components,
    'single_dpv':single_dpv_components,
    'single_swv':single_swv_components,
    'standard_addition_cv':standard_addition_cv_components,
    'standard_addition_lv':standard_addition_lv_components,
    'standard_addition_dpv':standard_addition_dpv_components,
    'standard_addition_swv':standard_addition_swv_components,
    'hg_au_electrode_plating':hg_au_electrode_plating_components,
    'hg_au_electrode_testing':hg_au_electrode_testing_components,
    }
    
@app.callback(
    visibility_outputs,
    [Input('program_selection','value')],
    visibility_states)
def update_program(value, update, update_acknowledged, first_update, *visibility_controlled_components):
    visibility_controlled_components = list(visibility_controlled_components)
    if update == update_acknowledged:
        write_config([{'component':'program_selection',
                       'attribute':'value','value':value}])
        
        component_list = component_lists[value] 
        output = [no_update, no_update]
        for i in range(len(visibility_controlled_components_labels)):
            if visibility_controlled_components_labels[i] in component_list:
                if visibility_controlled_components[i] == None:
                    output.append({'display':'flex'})
                else:
                    visibility_controlled_components[i]['display']='flex'
                    output.append(visibility_controlled_components[i])
            else:
                if visibility_controlled_components[i] == None:
                    output.append({'display':'none'})
                else:
                    visibility_controlled_components[i]['display']='none'
                    output.append(visibility_controlled_components[i])
        
        return output
        
    elif first_update == 1 and value != None:
        write_config([{'component':'program_selection',
                       'attribute':'value','value':value}])
        
        component_list = component_lists[value] 
        output = [update, 2]
        for i in range(len(visibility_controlled_components_labels)):
            if visibility_controlled_components_labels[i] in component_list:
                if visibility_controlled_components[i] == None:
                    output.append({'display':'flex'})
                else:
                    visibility_controlled_components[i]['display']='flex'
                    output.append(visibility_controlled_components[i])
            else:
                if visibility_controlled_components[i] == None:
                    output.append({'display':'none'})
                else:
                    visibility_controlled_components[i]['display']='none'
                    output.append(visibility_controlled_components[i])
        
        return output
        
    else:
        return [update, no_update]+visibility_controlled_components
        