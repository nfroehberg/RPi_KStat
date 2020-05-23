# Control backend for the KStat electrochemical analyzer GUI
# Mercury plating procedure for fabrication of Hg/Au electrodes
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

s_plate = scheduler(time,sleep)
def hg_au_electrode_plating(config, motor, ser):
    controls_disabled(True)
    write_config([{'component':'purge_switch','attribute':'on','value':False},
                  {'component':'stirr_switch','attribute':'on','value':True},
                  {'component':'scan_progress','attribute':'value','value':0}])
                    
    plating_time=config['plating_time_input']['value']
    plating_potential=config['plating_potential_input']['value']
    
    print('Start mercury plating at {} mV for {} s.'.format(plating_potential,plating_time))
    
    KStat.abort(ser)
    s_plate.enter(0,1,KStat.idle,(ser,plating_potential))
    s_plate.enter(0,2,write_config,([{'component':'scan_progress_label','attribute':'children','value':'Plating'}],))
    s_plate.enter(plating_time,1,KStat.abort,(ser,))
    s_plate.enter(plating_time,2,KStat.idle,(ser,0))
    s_plate.enter(plating_time,3,write_config,([{'component':'scan_progress_label','attribute':'children','value':''}],))
    for i in range(plating_time*4+1):
        s_plate.enter(i/4,1,make_scan_progress,(i,plating_time*4)) # progress bar
    s_plate.run()  
    
    write_config([{'component':'purge_switch','attribute':'on','value':config['purge_switch']['on']},
                    {'component':'stirr_switch','attribute':'on','value':config['stirr_switch']['on']},])
    controls_disabled(False)