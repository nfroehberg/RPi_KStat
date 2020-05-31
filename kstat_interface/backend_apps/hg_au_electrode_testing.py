# Control backend for the KStat electrochemical analyzer GUI
# Testing Hg/Au Electrodes through a series of cyclic voltammetric measurements
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
from os import remove
from .. import redis_config
from .single_cv import cv_measurement

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

def hg_au_electrode_testing(config, motor, ser):
    # disable user controls 
    controls_disabled(True)
    write_config([{'component':'scan_progress','attribute':'value','value':0}])
    
    id = config['popup_measurement_id']['value']
    n_tests = config['n_electrode_tests_input']['value']
    
    
    file_options = config['scan_selector']['options']
    # all but the last test scan are executed, shown, then deleted
    for i in range(n_tests-1):
        file = root.working_directory + id + '_test' + str(i+1)
        prog = (i/n_tests)*100
        write_config([{'component':'series_progress','attribute':'value','value':prog},
                      {'component':'series_progress_label','attribute':'children','value':'Test {}/{}'.format(i+1,n_tests)}])
        
        cv_measurement(config, motor, ser, file)
        
        if i == 0:
            file_options.append({'label':id + '_test' + str(i+1),'value':file+'.csv'})
        else:
            file_options[-1]={'label':id + '_test' + str(i+1),'value':file+'.csv'}
        write_config([{'component':'scan_selector','attribute':'options','value':file_options},
                      {'component':'scan_selector','attribute':'value','value':file+'.csv'}])
        # delete previous scan
        if i > 0:
            files = glob('{}/*'.format(root.working_directory))
            for scan in files:
                if (id + '_test' + str(i)) in scan:
                    remove(scan)
  
    prog = ((n_tests-1)/n_tests)*100
    file = root.working_directory + id
    write_config([{'component':'series_progress','attribute':'value','value':prog},
                  {'component':'series_progress_label','attribute':'children','value':'Test {}/{}'.format(n_tests,n_tests)}])
    
    cv_measurement(config, motor, ser, file)
    
    write_config([{'component':'series_progress','attribute':'value','value':100}])
    files = glob('{}/*'.format(root.working_directory))
    for scan in files:
        if (id + '_test' + str(n_tests-1)) in scan:
            remove(scan)

    KStat.idle(ser,0)
    
    # reenable user controls
    file_options[-1]={'label':id,'value':file+'.csv'}
    write_config([{'component':'purge_switch','attribute':'on','value':config['purge_switch']['on']},                    
                  {'component':'stirr_switch','attribute':'on','value':config['stirr_switch']['on']},
                  {'component':'scan_selector','attribute':'options','value':file_options},
                  {'component':'scan_selector','attribute':'value','value':file+'.csv'}])
    controls_disabled(False)