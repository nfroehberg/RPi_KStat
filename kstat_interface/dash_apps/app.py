# GUI Frontend for the KStat electrochemical analyzer
# This script provides the dash app instance as well as functions for writing to config etc.
# using Dash by Plotly (MIT licensed)
# Nico Fröhberg, 2019
# nico.froehberg@gmx.de

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
from time import time,sleep

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
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

def write_config(change_list: list):
    try:
        root.flush()
        config=literal_eval(str(root.config))
        for element in change_list:
            config[element['component']][element['attribute']] = element['value']
        root.update_timestamp = time()
        root.config = config
    except Exception as e:
        print(e)
        print("Couldn't write config, trying again.")
        sleep(1)
        return write_config(change_list)


