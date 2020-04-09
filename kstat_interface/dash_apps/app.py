import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import no_update
from glob import glob
from redisworks import Root
from .. import redis_config
from time import time
import os, shutil, base64

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>KStat Control</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# update individual paramaeters of config file
# pass arguments as list of changes where every change is a dictionary
# {'component','attribute','value'}
from ast import literal_eval
import json

def write_config(change_list: list):
    try:
        root.flush()
        program = str(root.program)
        config = literal_eval(str(root[program]))
        for element in change_list:
            config[element['component']][element['attribute']] = element['value']
        root[program] = config
        root[program+'_timestamp'] = time()
    except Exception as e:
        print(e)
        print("Couldn't write config, trying again.")
        return write_config(change_list)


def directory_and_scan_selection():
    return [
        dcc.Interval(id='directory_and_scan_initialization',disabled=False),
        dcc.Store(id='files_initialization'),
        dcc.Store(id='scan_selector_placeholder'),
        dcc.Dropdown(id='scan_selector',
            style={'width':'250px','color':'black'},
            clearable=False),
        html.Div(style={'width':'100px'}),
        html.P(id='directory_text',
            children='Directory',
            style={'paddingTop':'15px','width':'200px','overflowWrap':'break-word'}),
        html.Button( id='change_directory_button',
            style={'fontSize':'xx-large','border': '0',
                   'marginLeft':'10px'},
            children=u"\U0001F5C1"),
        dcc.Store('directory_popup_placeholder1'), #used to open popup
        dcc.Store('directory_popup_placeholder2'), #used to close popup and confirm directory change
        dcc.Store('directory_popup_placeholder3'), #used to close popup and cancel directory change
        dbc.Modal(id='directory_popup',
            centered=True,
            children=[
                dbc.ModalHeader("Select Working Directory"),
                dbc.ModalBody(
                    children=[
                        html.H6(id='directory_label'),
                        dcc.RadioItems(id='directory_selection',
                            inputStyle={'visibility':'hidden'},
                            labelStyle={'display':'block'},
                            ),
                        dcc.Input(id='new_directory_input',
                            placeholder='New Directory',
                            type='text',
                            style={'marginLeft':'20px','backgroundColor':'transparent','color':'rgb(200, 200, 200)','paddingLeft':'25px'},
                            debounce=True
                            ),
                        dcc.Store(id='new_directory_update'),
                        dcc.Store(id='working_directory_update'),
                        dcc.Store(id='files_update'),
                        html.H6(children='Files:'),
						dcc.Checklist(id='directory_file_list',
                            style={'marginLeft':'20px'},
                            labelStyle={'display':'block'}),
                        dcc.Checklist(id='directory_file_list_select_all',
                            style={'fontStyle':'italic','marginLeft':'20px'},
                            options=[{'label':'select all files','value':'all'}]),
                        ]),
                dbc.ModalFooter(
                    children=[
                        dcc.Store(id='original_working_directory'),
                        html.Button(children='delete file(s)',id='delete_files_button', style={'padding':'5px'}),
                        dcc.Store(id='delete_files_update'),
                        dcc.ConfirmDialog(id='delete_files_confirmation',
                            message='Delete the selected file(s)?'),
                        html.Button(children='delete directory',id='delete_directory_button', style={'padding':'5px'}),
                        dcc.Store(id='delete_directory_update'),
                        dcc.ConfirmDialog(id='delete_directory_confirmation',
                            message='Delete the current working directory and all its content?'),
                        dcc.ConfirmDialog(id='delete_directory_error',
                            message='The "data" directory cannot be deleted.'),
                        html.Button(children='cancel',id='directory_cancel_button'),
                        html.Button(children='confirm',id='directory_confirm_button'),
                    ])
                ]
            ),
        html.Button(id='upload_button',
            style={'fontSize':'xx-large','border': '0',
                   'marginLeft':'10px'},
            children=u"\U000021A5"),
        dcc.Store(id='upload_popup_placeholder1'),
        dcc.Store(id='upload_popup_placeholder2'),
        dbc.Modal(id='upload_popup',
            centered=True,
            children=[
                dbc.ModalHeader(id='upload_popup_header'),
                dbc.ModalBody(
                    children=[
                        dcc.Upload(id='upload_dialog',
                            children='drag and drop or select a file', 
                            multiple=True,
                            style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center'
                            })
                        ]),
                dbc.ModalFooter('Include data .csv file as well as the measurement parameters .txt file!')
                ]),
        html.Button(id='download_button',
            style={'fontSize':'xx-large','border': '0',
                   'marginLeft':'10px'},
            children=u"\U00002913"),
        dcc.Store(id='download_popup_placeholder1'),
        dcc.Store(id='download_popup_placeholder2'),
        dbc.Modal(id='download_popup',
            centered = True,
            children=[
                dbc.ModalHeader(),
                dbc.ModalBody(),
                dbc.ModalFooter()])
        ]

# open modal popup for the file download
@app.callback(
    Output('download_popup_placeholder1','data'),
    [Input('download_button','n_clicks')])
def openDownloadPopup(n_clicks):
    if n_clicks != None:
        return 'open'
    else:
        raise PreventUpdate
# since the modal popup is opened by one button and closed by another,
# two placeholder components are used to control its open state
@app.callback(
    [Output('download_popup','is_open')],
    [Input('download_popup_placeholder1','data'),
     Input('download_popup_placeholder2','data')])
def open_close_download_popup(placeholder1,placeholder2):
    #determining which input was triggered to determine whether to open or close the modal
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if trigger_id == 'download_popup_placeholder1':
        return [True]
    elif trigger_id == 'download_popup_placeholder2':
        return [False]
    else:
        return [False]


# open modal popup for the file upload
@app.callback(
    Output('upload_popup_placeholder1','data'),
    [Input('upload_button','n_clicks')])
def openUploadPopup(n_clicks):
    if n_clicks != None:
        return 'open'
    else:
        raise PreventUpdate
# since the modal popup is opened by one button and closed by another,
# two placeholder components are used to control its open state
@app.callback(
    [Output('upload_popup','is_open'),
    Output('upload_popup_header','children')],
    [Input('upload_popup_placeholder1','data'),
     Input('upload_popup_placeholder2','data')])
def open_close_upload_popup(placeholder1,placeholder2):
    #determining which input was triggered to determine whether to open or close the modal
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if trigger_id == 'upload_popup_placeholder1':
        header = 'Upload files to ' + (str(root.working_directory).replace(str(root.main_directory),'')).rstrip('/')
        return [True, header]
    elif trigger_id == 'upload_popup_placeholder2':
        return [False, no_update]
    else:
        return [False, no_update]

@app.callback(
    Output('upload_popup_placeholder2','data'),
    [Input('upload_dialog','contents')],
    [State('upload_dialog','filename')])
def uploadFile(contents,filenames):
    for i in range(len(contents)):
        content = contents[i]
        content_type, content_string = content.split(',')
        filename = filenames[i]
        with open(os.path.join(str(root.working_directory), filename), 'wb') as f:
            f.write(base64.b64decode(content_string))
    return 'close'

# delete all files selected in the list in the directory dialog after confirmation by the user
@app.callback(
    Output('delete_files_confirmation','displayed'),
    [Input('delete_files_button','n_clicks')])
def openDeleteFilesBox(n_clicks):
    if n_clicks != None:
        return True
    else:
        raise PreventUpdate
@app.callback(
    Output('delete_files_update','data'),
    [Input('delete_files_confirmation','submit_n_clicks')],
    [State('directory_file_list','value')])
def deleteFiles(n_clicks,files):
    if n_clicks != None:
        for file in files:
            file_parameters=file.replace('.csv','')+'-parameters.txt'
            file_plot=file.replace('.csv','')+'.png'
            if os.path.exists(file):
                os.remove(file)
            if os.path.exists(file_parameters):
                os.remove(file_parameters)
            if os.path.exists(file_plot):
                os.remove(file_plot)
        return time()
    else:
        raise PreventUpdate
    
# delete the current working directory and set to parent after user confirmation
@app.callback(
    [Output('delete_directory_confirmation','displayed'),
    Output('delete_directory_error','displayed')],
    [Input('delete_directory_button','n_clicks')])
def openDeleteDirectoryBox(n_clicks):
    if n_clicks != None:
        if root.working_directory == root.data_directory:
            return [False,True]
        else:
            return [True,False]
    else:
        raise PreventUpdate
@app.callback(
    Output('delete_directory_update','data'),
    [Input('delete_directory_confirmation','submit_n_clicks')])
def deleteDirectory(n_clicks):
    if n_clicks != None:
        if os.path.exists(str(root.working_directory)):
            shutil.rmtree(str(root.working_directory))
            p_dir = str(root.working_directory).rstrip('/')
            root.working_directory = p_dir[0:p_dir.rfind('/')+1]
            root.flush()
        return time()
    else:
        raise PreventUpdate

# slect/deselct all files in directory dialog to delete
@app.callback(
    Output('directory_file_list','value'),
    [Input('directory_file_list_select_all','value')],
    [State('directory_file_list','options')])
def selectAllFiles(value,options):
    if 'all' in value:
        new_value=[]
        for option in options:
            new_value.append(option['value'])
        return new_value
    else:
        return [None]
        
# create new subdirectory
@app.callback(
    Output('new_directory_update','data'),
    [Input('new_directory_input','value')])
def createDir(dir):
    dir = root.working_directory + dir + '/'
    if not os.path.exists(dir):
        os.mkdir(dir)
    return time()
    
# reload list of files on page reload
@app.callback(
    [Output('files_initialization','data'),
    Output('directory_and_scan_initialization','disabled')],
    [Input('directory_and_scan_initialization','n_intervals')])
def initializeFiles(n_intervals):
    return [time(),True]
    
# open modal popup for the user to select the working directory
@app.callback(
    Output('directory_popup_placeholder1','data'),
    [Input('change_directory_button','n_clicks')])
def openDirectoryPopup(n_clicks):
    if n_clicks != None:
        return 'open'
    else:
        raise PreventUpdate

# close modal popup after directory change
@app.callback(
    Output('directory_popup_placeholder2','data'),
    [Input('directory_confirm_button','n_clicks')])
def confirmDirectoryChange(n_clicks):
    if n_clicks != None:
        return 'close'

# close modal popup and reset working directory 
@app.callback(
    Output('directory_popup_placeholder3','data'),
    [Input('directory_cancel_button','n_clicks')])
def cancelDirectoryChange(n_clicks):
    if n_clicks != None:
        return 'close'
  
# since the modal popup is opened by one button and closed by another,
# two placeholder components are used to control its open state
@app.callback(
    [Output('files_update','data'),
     Output('directory_selection','value'),
     Output('original_working_directory','data'),
     Output('directory_popup','is_open')],
    [Input('directory_popup_placeholder1','data'),
     Input('directory_popup_placeholder2','data'),
     Input('directory_popup_placeholder3','data')],
     [State('original_working_directory','data')])
def open_close_directory_popup(placeholder1,placeholder2,placeholder3,original_working_directory):
    #determining which input was triggered to determine whether to open or close the modal
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if trigger_id == 'directory_popup_placeholder1':
        return [time(), None, str(root.working_directory), True]
    elif trigger_id == 'directory_popup_placeholder2':
        return [no_update, no_update, no_update, False]
    elif trigger_id == 'directory_popup_placeholder3':
        root.working_directory = original_working_directory
        return [time(), None, no_update, False]
    else:
        return [no_update, no_update, no_update, False]

@app.callback(
    [Output('scan_selector','options'),
    Output('directory_selection','options'),
	Output('directory_file_list','options'),
    Output('directory_text','children')],
    [Input('working_directory_update','data'),
    Input('files_update','data'),
    Input('files_initialization','data'),
    Input('new_directory_update','data'),
    Input('delete_files_update','data'),
    Input('delete_directory_update','data')])
def update_dropdowns(update_dirs,update_files,initialize_files,new_dir,delete_files,delete_directory):
    root.flush()
    
    directory_list = glob('{}*/'.format(root.working_directory))
	#don't allow user to go higher than the base data directory
    if root.working_directory != root.data_directory:
        directory_options=[{'label':u"\U00002B11"+' parent directory','value':str(root.working_directory)+'parent'}]
    else:
        directory_options=[]
	
	#generate list of subdirectories in current working directory
    for directory in directory_list:
        label = directory.replace(str(root.working_directory),'').strip('/')
        label = u"\U0001F5C1" + " " + label
        directory_options.append({'label':label,'value':directory})
	
	#generate list of csv files for scan selector
    file_list = glob('{}*.csv'.format(root.working_directory))
    file_options = []
    for file in file_list:
        label=file.replace(str(root.working_directory),'').replace('.csv','')
        file_options.append({'label':label,'value':file})
    
    label=str(root.working_directory).replace(str(root.main_directory),'').strip('/')
    return[file_options, directory_options, file_options, label]
 
@app.callback(
    [Output('directory_label','children'),
    Output('working_directory_update','data')],
    [Input('directory_selection','value')])
def select_directory(dir):
    if dir != None:
        if dir[-6:] == 'parent':
            # remove last directory from working directory path to go up one level
            p_dir = str(root.working_directory).rstrip('/')
            root.working_directory = p_dir[0:p_dir.rfind('/')+1]
        else:
            root.working_directory = dir
        root.flush()
        label=str(root.working_directory).replace(str(root.main_directory),'').strip('/')
        return [label, time()]
    else:
        label=str(root.working_directory).replace(str(root.main_directory),'').strip('/')
        return [label, no_update]

@app.callback(
    Output('scan_selector_placeholder','data'),
    [Input('scan_selector','value')])
def select_scan(value):
    if value != None:
        write_config([{'component':'graph_file','attribute':'data','value':value},
                      {'component':'start_button_go','attribute':'scan_id','value':value.strip(str(root.working_directory)).strip('.csv')}])
    raise PreventUpdate
        
