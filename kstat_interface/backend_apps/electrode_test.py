from time import time, sleep
from ..dash_apps.app import write_config
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

# initial config
config={}
config['placeholder']={'on':False}
config['graph_file']={'data':'/home/pi/KStat/data/NF30.csv'}
config['start_button_go']={'triggered':False,'scan_id':'no id'}
config['start_button']={'disabled':False} 
config['cancel_button']={'triggered':False,'disabled':True}
config['stirr_switch']={'on':False, 'disabled':False}
config['stirr_speed_slider']={'value':1000, 'disabled':False}
config['purge_switch']={'on':False, 'disabled':False, 'stored_on':False}
config['progress_bar']={'value':0}
config['scan_indicator']={'value':False}
config['cleaning_potential_input']={'value':-900}
config['cleaning_time_input']={'value':5}
config['deposition_potential_input']={'value':-100}
config['deposition_time_input']={'value':2}
config['start_potential_input']={'value':-100}
config['vertex1_potential_input']={'value':-1850}
config['vertex2_potential_input']={'value':-100}
config['slope_input']={'value':500}
config['samplefreq_input']={'value':'1KHz','triggered':False}
config['iv_gain_input']={'value':'POT_GAIN_300K','triggered':False}
config['PGA_gain_input']={'value':2,'triggered':False}
config['n_scans_input']={'value':1}
config['n_blanks_input']={'value':30}

def initial_config():
    return config

def check_config(motor,ser):
    try:
        root.flush()
        config = literal_eval(str(root.electrode_test))
    except Exception as e:
        print("Couldn't load config, trying again.")
        return False
    
    # stirring control
    if config['stirr_switch']['on'] and config['stirr_speed_slider']['value']!=None:
        motor.start('B', config['stirr_speed_slider']['value']/25)
    else:
        motor.start('B', 0)

    # purge control   
    if config['purge_switch']['on']:
        motor.activate('A')
    else:
        motor.deactivate('A')

    # measurement
    if config['start_button_go']['triggered']:
        write_config([{'component':'start_button_go',
                       'attribute':'triggered','value':False}])
        global measurement
        measurement = Process(target=cv_measurement,
                          args=(ser,
                                config['cleaning_potential_input']['value'],
                                config['cleaning_time_input']['value'],
                                config['deposition_potential_input']['value'],
                                config['deposition_time_input']['value'],
                                config['start_potential_input']['value'],
                                config['vertex1_potential_input']['value'],
                                config['vertex2_potential_input']['value'],
                                config['slope_input']['value'],
                                config['start_button_go']['scan_id'],
                                config['samplefreq_input']['value'],
                                config['iv_gain_input']['value'],
                                config['PGA_gain_input']['value'],
                                config['n_scans_input']['value'],
                                config['n_blanks_input']['value']))
        measurement.start()
    if config['cancel_button']['triggered']:
        print('Cancel')
        write_config([{'component':'cancel_button',
                       'attribute':'triggered','value':False}])
        measurement.terminate()
        cancel_measurement(ser)

    if config['iv_gain_input']['triggered']:
        write_config([{'component':'iv_gain_input','attribute':'triggered','value':False}])
        KStat.abort(ser)
        KStat.setGain(ser,config['iv_gain_input']['value'])


    if config['PGA_gain_input']['triggered'] or config['samplefreq_input']['triggered']:
        write_config([{'component':'PGA_gain_input','attribute':'triggered','value':False},
                      {'component':'samplefreq_input','attribute':'triggered','value':False}])
        KStat.abort(ser)
        KStat.setupADC(ser, 1, config['samplefreq_input']['value'], config['PGA_gain_input']['value'])
        
    return True

s_measurement = scheduler(time,sleep)
s_progress = scheduler(time,sleep)
progr = Thread(target=s_progress.run)
def cv_measurement(ser,cleaning_potential,cleaning_time,deposition_potential,
                   deposition_time,start_potential,vertex1_potential,
                   vertex2_potential,slope,scan_id,samplefreq,iv_gain,PGA_gain,n_scans,n_blanks):
    # deactivate controls during plating procedure
    write_config(
        [{'component':'scan_indicator',
          'attribute':'value','value':True},
         {'component':'start_button',
          'attribute':'disabled','value':True},
         {'component':'cancel_button',
          'attribute':'disabled','value':False},
         {'component':'purge_switch',
          'attribute':'disabled','value':True},
         {'component':'purge_switch',
          'attribute':'on','value':False},
         {'component':'purge_switch', # store state of purging switch to restore after plating
          'attribute':'stored_on','value':root['single_CV']['purge_switch']['on']}])

    total_time = cleaning_time + deposition_time + (abs(vertex1_potential-start_potential)/slope + abs(vertex1_potential-vertex2_potential)/slope)*n_scans
    file = '/home/pi/KStat/data/'+scan_id
    # start measurement procedure on KStat
    KStat.abort(ser)
    for i in range(n_blanks):
        blank_id = '/home/pi/KStat/data/blank ' + str(i)
        s_measurement.enter(0,1,KStat.cyclicVoltammetry,(
            ser,PGA_gain,iv_gain,cleaning_time,deposition_time,cleaning_potential,
            deposition_potential,vertex1_potential,vertex2_potential,
            start_potential,n_scans,slope,samplefreq,blank_id,True))
        s_measurement.enter(0,1,write_config,([{'component':'graph_file',
                                                'attribute':'data',
                                                'value':blank_id+'.csv'},
                                               {'component':'start_button_go',
                                                'attribute':'scan_id',
                                                'value':'Blank '+str(i)},
                                               {'component':'progress_bar',
                                                'attribute':'value',
                                                'value':(i/(n_blanks+1))*100}],))
    s_measurement.enter(0,1,KStat.cyclicVoltammetry,(
        ser,PGA_gain,iv_gain,cleaning_time,deposition_time,cleaning_potential,
        deposition_potential,vertex1_potential,vertex2_potential,
        start_potential,n_scans,slope,samplefreq,file,True))
    s_measurement.run()
    
    # reactivate controls after completion
    write_config(
        [{'component':'scan_indicator',
          'attribute':'value','value':False},
         {'component':'start_button',
          'attribute':'disabled','value':False},
         {'component':'cancel_button',
          'attribute':'disabled','value':True},
         {'component':'purge_switch',
          'attribute':'disabled','value':False},
         {'component':'graph_file',
          'attribute':'data','value':file+'.csv'},
         {'component':'start_button_go',
          'attribute':'scan_id','value':scan_id},
         {'component':'progress_bar',
          'attribute':'value','value':100},
         {'component':'purge_switch',
          'attribute':'on','value':root['single_CV']['purge_switch']['stored_on']}])
    for i in range(n_blanks):
        remove('/home/pi/KStat/data/blank ' + str(i)+'.csv')
        remove('/home/pi/KStat/data/blank ' + str(i)+'-parameters.txt')

    
def cancel_measurement(ser):
    progr._stop()
    KStat.abort(ser)
    write_config([{'component':'scan_indicator',
                   'attribute':'value','value':False},
                  {'component':'start_button',
                   'attribute':'disabled','value':False},
                  {'component':'cancel_button',
                   'attribute':'disabled','value':True},
                  {'component':'purge_switch',
                   'attribute':'disabled','value':False},
                  {'component':'purge_switch',
                   'attribute':'on','value':root.hg_plater['purge_switch']['stored_on']}])
    print('Cancelled Measurement.')
