# Control backend for the KStat electrochemical analyzer GUI
# Manual movement control of the profiler
# Nico Fröhberg, 2020
# nico.froehberg@gmx.de

from time import time, sleep
from sched import scheduler
from multiprocessing import Process
from threading import Thread
from redisworks import Root
from .. import redis_config
from kstat_interface.dash_apps.app import write_config

redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

def profiler_home(config,profiler,mm):
    print('Homing triggered')
    
    max_speed = config['max_speed_input']['value'] * mm * 10000
    max_acceleration = config['max_acceleration_input']['value'] * mm * 100
    profiler.set_max_speed(max_speed)
    profiler.set_max_acceleration(max_acceleration)
    profiler.set_max_deceleration(max_acceleration)
    speed = config['max_speed_input']['value'] * mm * 10000 * -1
    profiler.move_to_limit(speed)
    position = 'Profiler Position: {:05.1f} mm'.format(profiler.get_current_position()/mm)
    write_config([{'component':'start_button','attribute':'disabled','value':False},
                    {'component':'home_button','attribute':'disabled','value':False},
                    {'component':'move_step_button','attribute':'disabled','value':False},
                    {'component':'profiler_position','attribute':'children','value':position},])
    
def profiler_move_step(config,profiler,mm):
    print('Step Move triggered')
    
    max_speed = config['max_speed_input']['value'] * mm * 10000
    max_acceleration = config['max_acceleration_input']['value'] * mm * 100
    profiler.set_max_speed(max_speed)
    profiler.set_max_acceleration(max_acceleration)
    profiler.set_max_deceleration(max_acceleration)
    target = config['profile_step_distance_input']['value']
    target = profiler.get_current_position() + int(target*mm)
    profiler.move_to_position(target)
    position = 'Profiler Position: {:05.1f} mm'.format(profiler.get_current_position()/mm)
    write_config([{'component':'start_button','attribute':'disabled','value':False},
                    {'component':'home_button','attribute':'disabled','value':False},
                    {'component':'move_step_button','attribute':'disabled','value':False},
                    {'component':'profiler_position','attribute':'children','value':position},])