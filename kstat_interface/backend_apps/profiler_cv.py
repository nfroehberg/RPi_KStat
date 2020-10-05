# Control backend for the KStat electrochemical analyzer GUI
# Vertical CV profiling
# Nico Fröhberg, 2020
# nico.froehberg@gmx.de 

from time import time, sleep
from ..dash_apps.app import write_config, make_scan_progress, controls_disabled
from .drivers import KStat_0_1_driver as KStat
from serial import Serial
from sched import scheduler
from multiprocessing import Process
from threading import Thread
from redisworks import Root
from ast import literal_eval
from glob import glob
import os
from .. import redis_config
from .single_cv import cv_measurement
 

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0) 

def profiler_cv(config,motor,ser,profiler,mm):
    controls_disabled(True)
    print('Profiler CV triggered')
    
    n_steps = config['profile_step_number_input']['value']
    step_distance = config['profile_step_distance_input']['value']
    n_replicates = config['profile_repeat_measurements_input']['value']
    max_speed = config['max_speed_input']['value'] * mm * 10000
    max_acceleration = config['max_acceleration_input']['value'] * mm * 100
    #profiler.set_max_speed(max_speed)
    #profiler.set_max_acceleration(max_acceleration)
    #profiler.set_max_deceleration(max_acceleration)
    
    # create directory for scans
    profile_id = config['popup_measurement_id']['value']
    root.flush()
    dir = root.working_directory + profile_id + '/'
    p_dir = str(root.working_directory).rstrip('/')
    w_dir = p_dir[p_dir.rfind('/')+1:]
    if w_dir != profile_id:
        if not os.path.exists(dir):
            os.mkdir(dir)
        root.working_directory = dir
        write_config([{'component':'directory_and_scan_refresher','attribute':'data','value':time()}])
    
    write_config([{'component':'series_progress','attribute':'value','value':(1/(n_steps+1))},
                  {'component':'series_progress_label','attribute':'children','value':'Measurement {}/{}'.format(1,n_steps+1)}])
    # first measurement at initial position
    #position = profiler.get_current_position()/mm
    position = 7
    for i in range(n_replicates):
        write_config([{'component':'series_progress_label','attribute':'children','value':'Measurement {}/{} - Scan {}/{}'.format(1,n_steps+1,i+1,n_replicates)},
                        {'component':'series_progress','attribute':'value','value':(1/(n_steps+1))*100},])
        scan_id = '_step000_{:05.1f}mm_{:02.0f}'.format(position,i+1)
        file = root.working_directory + profile_id + scan_id
        cv_measurement(config, motor, ser, file)
        root.flush()
        file_options = literal_eval(str(root.config))['scan_selector']['options']
        file_options.append({'label':profile_id+scan_id,'value':file+'.csv'})
        write_config([{'component':'scan_selector','attribute':'options','value':file_options},
                        {'component':'scan_selector','attribute':'value','value':file+'.csv'}])
    for i in range(n_steps):
        # move electrode
        write_config([{'component':'scan_progress_label','attribute':'children','value':'Moving Sensor'},
                        {'component':'series_progress','attribute':'value','value':((i+2)/(n_steps+1))*100},
                        {'component':'series_progress_label','attribute':'children','value':'Measurement {}/{}'.format(i+2,n_steps+1)},])
        #target = profiler.get_current_position() + int(target*mm)
        #profiler.move_to_position(target)
        sleep(3)
        #position = profiler.get_current_position()/mm
        position = step_distance * (i+1)
        position_text = 'Profiler Position: {:05.1f} mm'.format(position)
        write_config([{'component':'profiler_position','attribute':'children','value':position_text},])
        # measurements
        for j in range(n_replicates):
            write_config([{'component':'series_progress_label','attribute':'children','value':'Measurement {}/{} - Scan {}/{}'.format(i+2,n_steps+1,j+1,n_replicates)}])
            scan_id = '_step{:03.0f}_{:05.1f}mm_{:02.0f}'.format(i+1,position,j+1)
            file = root.working_directory + profile_id + scan_id
            cv_measurement(config, motor, ser, file)
            root.flush()
            file_options = literal_eval(str(root.config))['scan_selector']['options']
            file_options.append({'label':profile_id+scan_id,'value':file+'.csv'})
            write_config([{'component':'scan_selector','attribute':'options','value':file_options},
                            {'component':'scan_selector','attribute':'value','value':file+'.csv'}])
        
    controls_disabled(False)