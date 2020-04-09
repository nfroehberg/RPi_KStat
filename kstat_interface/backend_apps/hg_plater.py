from time import time, sleep
from ..dash_apps.app import write_config
from .drivers import KStat_0_1_driver as KStat
from serial import Serial
from sched import scheduler
from multiprocessing import Process
from redisworks import Root
from ast import literal_eval
from .. import redis_config

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

# initial config
config={}
config['placeholder']={'on':False}
config['stirr_switch']={'on':False, 'disabled':False}
config['stirr_speed_slider']={'value':1000, 'disabled':False}
config['purge_switch']={'on':False, 'disabled':False, 'stored_on':False}
config['plating_potential_input']={'value':-100, 'disabled':False}
config['plating_time_input']={'value':240, 'disabled':False}
config['progress_bar']={'value':0}
config['plating_button']={'triggered':False, 'disabled':False}
config['cancel_plating_button']={'triggered':False, 'disabled':True}
config['plating_indicator']={'value':False}

def initial_config():
    return config

# check for updates in hg_plater config based on timestamp at redis server
def check_config(motor,ser):
    try:
        root.flush()
        config = literal_eval(str(root.hg_plater))
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

    # plating
    if config['plating_button']['triggered'] == True:
        write_config([{'component':'plating_button',
                       'attribute':'triggered','value':False}])
        global plating
        plating = Process(target=hg_plating,
                          args=(ser,config['plating_potential_input']['value'],
                                config['plating_time_input']['value']))
        plating.start()
    elif config['cancel_plating_button']['triggered'] == True:
        print('Cancel')
        write_config([{'component':'cancel_plating_button',
                       'attribute':'triggered','value':False}])
        plating.terminate()
        cancel_plating(ser)
    return True

#################################################################################            

s_plate = scheduler(time,sleep)
def hg_plating(ser,plating_potential,plating_time):
    root.flush()
    # deactivate controls during plating procedure
    write_config([{'component':'plating_indicator',
                   'attribute':'value','value':True},
                  {'component':'plating_button',
                   'attribute':'disabled','value':True},
                  {'component':'cancel_plating_button',
                   'attribute':'disabled','value':False},
                  {'component':'purge_switch',
                   'attribute':'disabled','value':True},
                  {'component':'purge_switch',
                   'attribute':'on','value':False},
                  {'component':'purge_switch', # store state of purging switch to restore after plating
                   'attribute':'stored_on','value':root.hg_plater['purge_switch']['on']}])

    # start plating procedure on KStat
    print('Start plating at {}mV for {}s.'.format(plating_potential,plating_time))
    KStat.abort(ser)
    s_plate.enter(0,1,KStat.idle,(ser,plating_potential))
    s_plate.enter(plating_time,1,KStat.abort,(ser,))
    s_plate.enter(plating_time,1,KStat.idle,(ser,0))
    for i in range(plating_time+1):
        s_plate.enter(i,1,make_progress,(i,plating_time)) # progress bar
    start = time()
    s_plate.run()

    # reactivate controls after completion
    write_config([{'component':'plating_indicator',
                   'attribute':'value','value':False},
                  {'component':'plating_button',
                   'attribute':'disabled','value':False},
                  {'component':'cancel_plating_button',
                   'attribute':'disabled','value':True},
                  {'component':'purge_switch',
                   'attribute':'disabled','value':False},
                  {'component':'purge_switch',
                   'attribute':'on','value':root.hg_plater['purge_switch']['stored_on']}])
    print('finished plating for {:.2f} s.'.format(time()-start))

# update progress bar as current time to max time
def make_progress(t,max_t):
    prog = (t/max_t)*100
    write_config([{'component':'progress_bar',
                   'attribute':'value','value':prog}])

# cancel plating procedure and restore controls
def cancel_plating(ser):
    KStat.abort(ser)
    KStat.idle(ser,0)
    write_config([{'component':'plating_indicator',
                   'attribute':'value','value':False},
                  {'component':'plating_button',
                   'attribute':'disabled','value':False},
                  {'component':'cancel_plating_button',
                   'attribute':'disabled','value':True},
                  {'component':'purge_switch',
                   'attribute':'disabled','value':False},
                  {'component':'purge_switch',
                   'attribute':'on','value':root.hg_plater['purge_switch']['stored_on']}])
    print('Cancelled Plating.')
