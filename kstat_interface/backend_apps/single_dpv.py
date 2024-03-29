# Control backend for the KStat electrochemical analyzer GUI
# Single Differential Pulse Voltammetry Measurement Procedure
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
from .. import redis_config
from os import remove

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

def single_dpv(config, motor, ser):
    # disable controls
    controls_disabled(True)
    write_config([{'component':'scan_progress','attribute':'value','value':0}])
    
    id = config['popup_measurement_id']['value']
    file = root.working_directory + id
    
    dpv_measurement(config, motor, ser, file)
    
    KStat.idle(ser,0)
    
    file_options = config['scan_selector']['options']
    file_options.append({'label':id,'value':file+'.csv'})
    write_config([{'component':'purge_switch','attribute':'on','value':config['purge_switch']['on']},                    
                  {'component':'stirr_switch','attribute':'on','value':config['stirr_switch']['on']},
                  {'component':'scan_selector','attribute':'options','value':file_options},
                  {'component':'scan_selector','attribute':'value','value':file+'.csv'}])
    controls_disabled(False)

def dpv_measurement(config, motor, ser, file):
    # Stirr/Purge Controls, Progress Bar updates etc. need to run in separate thread so they can be executed in parallel to the KStat measurement
    s_auxiliary = scheduler(time,sleep)
    aux = Thread(target=s_auxiliary.run)
    s_measurement = scheduler(time,sleep)

    # get individual values out of config for better readability
    purge_time=config['purge_time_input']['value']
    cleaning_potential=config['cleaning_potential_input']['value']
    cleaning_time=config['cleaning_time_input']['value']
    deposition_potential=config['deposition_potential_input']['value']
    deposition_time=config['deposition_time_input']['value']
    start_potential=config['start_potential_input']['value']
    end_potential=config['end_potential_input']['value']
    pulse_height=config['pulse_height_input']['value']
    pulse_width=config['pulse_width_input']['value']
    period=config['period_input']['value']
    step_size=config['step_size_input']['value']
    samplefreq=config['samplefreq_input']['value']
    iv_gain=config['iv_gain_input']['value']
    pga_gain=config['pga_gain_input']['value']
    comment=config['comment_input']['value']

    scan_time = ((abs(start_potential-end_potential)/step_size)*period)/1000
    
    print('Start DPV Measurement')
    
    KStat.abort(ser)
    
    # purge and show purge time progress
    if purge_time > 0:
        s_auxiliary.enter(0,1,write_config,([{'component':'scan_progress_label','attribute':'children','value':'Purging'},
                                         {'component':'purge_switch','attribute':'on','value':True},
                                         {'component':'stirr_switch','attribute':'on','value':True}],))
        for i in range(purge_time*4+1):
            s_auxiliary.enter(i/4,1,make_scan_progress,(i+1,purge_time*4)) # progress bar
        s_auxiliary.enter(purge_time,1,write_config,([{'component':'purge_switch','attribute':'on','value':False},],))
    
    # after purging start measurement
    s_measurement.enter(purge_time,2,KStat.differentialPulseVoltammetry,(
        ser,pga_gain,iv_gain,cleaning_time,deposition_time,cleaning_potential,
        deposition_potential,start_potential,end_potential,step_size,
        pulse_height,period,pulse_width,samplefreq,file,comment,True))
    
    # show progress of cleaning
    if cleaning_time > 0:
        s_auxiliary.enter(purge_time,2,write_config,([{'component':'scan_progress_label','attribute':'children','value':'Cleaning'},],))
        for i in range(cleaning_time*4+1):
            s_auxiliary.enter(purge_time+(i/4),2,make_scan_progress,(i+1,cleaning_time*4)) # progress bar
            
    
    # show progress of cleaning
    if deposition_time > 0:
        s_auxiliary.enter(purge_time+cleaning_time,2,write_config,([{'component':'scan_progress_label','attribute':'children','value':'Deposition'},],))
        for i in range(deposition_time*4+1):
            s_auxiliary.enter(purge_time+cleaning_time+(i/4),2,make_scan_progress,(i+1,deposition_time*4)) # progress bar
        
    # After purging, cleaning and depositioning, turn off stirrer:
    s_auxiliary.enter(purge_time+cleaning_time+deposition_time,1,write_config,
                        ([{'component':'stirr_switch','attribute':'on','value':False},
                          {'component':'scan_progress_label','attribute':'children','value':'Scan'},],))
    for i in range(int(scan_time)*4+1):
            s_auxiliary.enter(purge_time+cleaning_time+deposition_time+(i/4),2,make_scan_progress,(i+1,scan_time*4)) # progress bar
                          
    
    aux.start()
    s_measurement.run() 