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
config['placeholder']={'stuff':'test'}

def initial_config():
    return config

def check_config(motor,ser):
    try:
        root.flush()
        config = literal_eval(str(root.single_DPV))
    except Exception as e:
        print("Couldn't load config, trying again.")
        return False
    
    return True
