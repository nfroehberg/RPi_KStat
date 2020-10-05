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
import os, base64
from shutil import copyfile

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
    
single_lsv_components = [
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
    
standard_addition_lsv_components = [
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
    
profiler_cv_components = [
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
    'scan_progress_container',
    'series_progress_container',
    'file_management',
    'comment_input_container',
    'start_button_container',
    'stop_button_container',
    'max_speed_input_container',
    'max_acceleration_input_container',
    'home_button_container',
    'move_step_button_container',
    ]
    
# method files are generated using component lists above. components from this list are excluded
component_exclusion_list=[
    'start_button_container',
    'stop_button_container',
    'graph_and_file_management',
    'voltammogram_graph_container',
    'purge_switch_container',
    'stirr_switch_container',
    'stirr_speed_slider_container',
    'scan_progress_container',
    'series_progress_container',
    'file_management']

def config_selection():
    return html.Div(id='config_selection_container',
        style={'width':'30%'},
        className='centered_row',
        children=[
            html.Button(id='config_selection_button',
                children='Method'),
            dcc.Store(id='open_config_selection_popup'),
            dcc.Store(id='close_config_selection_popup1'),
            dcc.Store(id='close_config_selection_popup2'),
            dbc.Modal(id='config_selection_popup',
                centered=True,
                children=[
                    dbc.ModalHeader('Method Selection'),
                    dbc.ModalBody(
                        className='centered_row',
                        children=[
                            dcc.Store(id='config_selection_dropdown_update1'),
                            dcc.Store(id='config_selection_dropdown_update2'),
                            dcc.Store(id='config_selection_dropdown_update3'),
                            dcc.Store(id='config_selection_dropdown_update4'),
                            dcc.Dropdown(id='config_selection_dropdown',
                                style={'width':'100%','color':'black'},
                                clearable=False),
                            html.Div(style={'width':'100%','height':'10px'}),
                            dcc.Input(id='new_method_input',
                                style={'width':'47.5%'},
                                placeholder='method_id'),
                            html.Div(style={'width':'5%'}),
                            html.Button(id='new_method_button',children='New Method',
                                style={'width':'47.5%'}),
                            html.Div(style={'width':'100%','height':'10px'}),
                            html.Button(id='update_method_button',children='Update Method',
                                style={'width':'47.5%'}),
                            dcc.Store(id='update_method_confirmation_placeholder'),
                            dcc.ConfirmDialog(id='update_method_confirmation',
                                message='Overwrite selected method with current settings?'),
                            dcc.ConfirmDialog(id='delete_method_confirmation',
                                message='Delete the selected method?'),
                            html.Div(style={'width':'5%'}),
                            html.Button(id='delete_method_button',children='Delete Method',
                                style={'width':'47.5%'}),
                            html.Div(style={'width':'100%','height':'10px'}),
                            html.A(id='download_method_button',children='Download Method',
                                style={'width':'47.5%','height': '42px','lineHeight': '45px',
                                'borderWidth': '1px','borderStyle': 'dashed',
                                'borderRadius': '5px','textAlign': 'center','color':'white'}),
                            html.Div(style={'width':'5%'}),
                            html.Div(style={'width':'47.5%'},
                                children=dcc.Upload(id='upload_method',children='Upload Method',
                                style={'width': '100%','height': '42px','lineHeight': '45px',
                                'borderWidth': '1px','borderStyle': 'dashed',
                                'borderRadius': '5px','textAlign': 'center'},
                                multiple=False))
                            ]),
                    dbc.ModalFooter(
                        className='centered_row',
                        children=[
                            html.Button(id='config_cancel_button',
                                children='Cancel',
                                style={'width':'46.5%'}),
                            html.Div(style={'width':'3%'}),
                            html.Button(id='config_confirm_button',
                                children='Confirm',
                                style={'width':'46.5%'}),
                            ])
                    ])
            ]
        )

@app.callback(
    Output('config_selection_dropdown_update4','data'),
    [Input('upload_method','contents')],
    [State('upload_method','filename')])
def upload_method_file(file,filename):
    if file != None:
        content_type, content_string = file.split(',')
        with open(os.path.join(str(root.methods_directory), filename), 'wb') as f:
            f.write(base64.b64decode(content_string))
        return time()
    else:
        raise PreventUpdate

@app.callback(
    [Output('download_method_button','href'),
     Output('download_method_button','download')],
    [Input('config_selection_dropdown','value')])
def generate_method_download(file):
    if file != None:
        target = str(root.download_directory) + file.replace(str(root.methods_directory),'')
        copyfile(file,target)
        link = '/user_downloads/{}'.format(target.replace(str(root.download_directory),''))
        return [link, file.replace(str(root.methods_directory),'')]
    else:
        raise PreventUpdate

@app.callback(
    Output('close_config_selection_popup2','data'),
    [Input('config_confirm_button','n_clicks')],
    [State('config_selection_dropdown','value')])
def apply_method_selection(n_clicks,file):
    if n_clicks != None and file != None:
        f = open(file,'r')
        lines = f.readlines()
        f.close()
        output = []
        for line in lines:
            line = line.split(',')
            component = line[0]
            value = line[1]
            try:
                value = int(value)
            except:
                pass
            output.append({'component':component,'attribute':'value','value':value})
        write_config(output)
        return True
    else:
        raise PreventUpdate

@app.callback(
    Output('delete_method_confirmation','displayed'),
    [Input('delete_method_button','n_clicks')],
    [State('config_selection_dropdown','value')])
def open_delete_method_confirmation(n_clicks,file):
    if n_clicks != None and file != None:
        return True
    else:
        raise PreventUpdate
@app.callback(
    Output('config_selection_dropdown_update3','data'),
    [Input('delete_method_confirmation','submit_n_clicks')],
    [State('config_selection_dropdown','value')])
def update_method(n_clicks,file):
    if n_clicks != None:
        if os.path.exists(file):
            os.remove(file)
        return time()
    else:
        raise PreventUpdate

@app.callback(
    Output('update_method_confirmation','displayed'),
    [Input('update_method_button','n_clicks')],
    [State('config_selection_dropdown','value')])
def open_update_method_confirmation(n_clicks,file):
    if n_clicks != None and file != None:
        return True
    else:
        raise PreventUpdate
@app.callback(
    Output('update_method_confirmation_placeholder','data'),
    [Input('update_method_confirmation','submit_n_clicks')],
    [State('config_selection_dropdown','value')])
def update_method(n_clicks,file):
    if n_clicks != None:
        root.flush()
        config = literal_eval(str(root.config))
        program = config['program_selection']['value']
        component_list = component_lists[program]
        components = []
        for component in component_list:
            if component not in component_exclusion_list:
                components.append(component.replace('_container',''))
        output = 'category_selection,{},\nprogram_selection,{},\n'.format(config['category_selection']['value'],config['program_selection']['value'])
        for component in components:
            output = output + '{},{},\n'.format(component,config[component]['value'])
        f = open(file,'w')
        f.write(output)
        f.close()
        raise PreventUpdate
    else:
        raise PreventUpdate

@app.callback(
    [Output('config_selection_dropdown_update2','data'),
     Output('config_selection_dropdown','value')],
    [Input('new_method_button','n_clicks')],
    [State('new_method_input','value')])
def create_new_method(n_clicks,id):
    if n_clicks != None and id != '':
        root.flush()
        config = literal_eval(str(root.config))
        program = config['program_selection']['value']
        component_list = component_lists[program]
        components = []
        for component in component_list:
            if component not in component_exclusion_list:
                components.append(component.replace('_container',''))
        output = 'category_selection,{},\nprogram_selection,{},\n'.format(config['category_selection']['value'],config['program_selection']['value'])
        for component in components:
            output = output + '{},{},\n'.format(component,config[component]['value'])
        file = str(root.methods_directory) + id + '.txt'
        f = open(file,'w')
        f.write(output)
        f.close()
        return [time(),file]
    else:
        raise PreventUpdate

@app.callback(
    Output('config_selection_dropdown','options'),
    [Input('config_selection_dropdown_update1','data'),
     Input('config_selection_dropdown_update2','data'),
     Input('config_selection_dropdown_update3','data'),
     Input('config_selection_dropdown_update4','data')])
def update_method_dropdown(update1,update2,update3,update4):
    ctx = dash.callback_context
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    method_files_list = glob('{}*.txt'.format(root.methods_directory))
    method_list = []
    for method_file in method_files_list:
        method_list.append({'label':(method_file.replace(str((root.methods_directory)),'')).replace('.txt',''),'value':method_file})
    return method_list

@app.callback(
    [Output('config_selection_popup','is_open'),
     Output('config_selection_dropdown_update1','data')],
    [Input('open_config_selection_popup','data'),
     Input('close_config_selection_popup1','data'),
     Input('close_config_selection_popup2','data')])
def open_close_config_selection(open,close1,close2):
    ctx = dash.callback_context
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'open_config_selection_popup':
        return [True, time()]
    elif trigger_id == 'close_config_selection_popup1':
        return [False, no_update]
    elif trigger_id == 'close_config_selection_popup2':
        return [False, no_update]

@app.callback(
    Output('open_config_selection_popup','data'),
    [Input('config_selection_button','n_clicks')])
def button_open_method_selection(n_clicks):
    if n_clicks != None:
        return time()
    else:
        raise PreventUpdate

@app.callback(
    Output('close_config_selection_popup1','data'),
    [Input('config_cancel_button','n_clicks')])
def button_cancel_method_selection(n_clicks):
    if n_clicks != None:
        return time()
    else:
        raise PreventUpdate

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
                    {'label':'Profiler','value':'profiler'},
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
    if value != None:
        if value == 'voltammetry_single':
            options = [
                {'label':'Cyclic','value':'single_cv'},
                {'label':'Linear Sweep','value':'single_lsv'},
                {'label':'Differential Pulse','value':'single_dpv'},
                {'label':'Squarewave','value':'single_swv'},]
        elif value == 'voltammetry_standard_addition':
            options = [
                {'label':'Cyclic','value':'standard_addition_cv'},
                {'label':'Linear Sweep','value':'standard_addition_lsv'},
                {'label':'Differential Pulse','value':'standard_addition_dpv'},
                {'label':'Squarewave','value':'standard_addition_swv'},]
        elif value == 'hg_au_electrode_fabrication':
            options = [
                {'label':'Mercury Plating','value':'hg_au_electrode_plating'},
                {'label':'Electrode Testing','value':'hg_au_electrode_testing'}]
        elif value == 'profiler':
            options = [{'label':'Cyclic Voltammetry Profile','value':'profiler_cv'}]
        else:
            options = []
        if update == update_acknowledged:
            write_config([{'component':'program_selection',
                           'attribute':'options','value':options},
                           {'component':'category_selection',
                           'attribute':'value','value':value}])
            return no_update
        else:
            write_config([{'component':'program_selection',
                           'attribute':'options','value':options}])
            return update
    else:
        raise PreventUpdate


    
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
    'single_lsv':single_lsv_components,
    'single_dpv':single_dpv_components,
    'single_swv':single_swv_components,
    'standard_addition_cv':standard_addition_cv_components,
    'standard_addition_lsv':standard_addition_lsv_components,
    'standard_addition_dpv':standard_addition_dpv_components,
    'standard_addition_swv':standard_addition_swv_components,
    'hg_au_electrode_plating':hg_au_electrode_plating_components,
    'hg_au_electrode_testing':hg_au_electrode_testing_components,
    'profiler_cv':profiler_cv_components,
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
        
    elif value != None:
        component_list = component_lists[value] 
        output = [update, no_update]
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
        raise PreventUpdate