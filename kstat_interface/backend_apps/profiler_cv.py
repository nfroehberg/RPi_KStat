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
from os import remove
from .. import redis_config
from .single_cv import cv_measurement


redis_host,redis_port = redis_config.get_config()
root = Root(host=redis_host, port=redis_port, db=0)

def profiler_cv(config,motor,ser,profiler):
    print('Profiler CV triggered')