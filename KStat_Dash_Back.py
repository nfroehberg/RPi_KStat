from kstat_interface.backend_apps.drivers.tb6612_motor_driver import TB6612
from time import sleep, time
import kstat_interface.backend_apps.drivers.KStat_0_1_driver as KStat
from serial import Serial
from sched import scheduler
from multiprocessing import Process
from redisworks import Root
from ast import literal_eval
from kstat_interface.dash_apps.app import write_config
import kstat_interface.backend_apps.hg_plater as hg_plater
import kstat_interface.backend_apps.single_CV as single_CV
import kstat_interface.backend_apps.single_DPV as single_DPV
import kstat_interface.backend_apps.electrode_test as electrode_test
from kstat_interface import redis_config

# Serial address of KStat at specific USB port
KStat_path = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0'

# start redisworks server and store initial config
def initialize_redis():
    global root
    redis_host,redis_port = redis_config.get_config()
    root = Root(host=redis_host, port=redis_port, db=0)

    root.startup={'test':1}
    
    root.hg_plater=hg_plater.initial_config()
    root.hg_plater_timestamp=time()
    
    root.electrode_test=electrode_test.initial_config()
    root.electrode_test_timestamp=time()

    root.single_CV=single_CV.initial_config()
    root.single_CV_timestamp=time()

    root.single_DPV=single_DPV.initial_config()
    root.single_DPV_timestamp=time()

# start motor driver for stirring motor and purge valve
def initialize_motor():
    global motor
    motor = TB6612()
    motor.standby(False)

# set up KStat potentiostat
def initialize_KStat():
    global ser
    ser = Serial(KStat_path, 9600, timeout = 1)
    ADSbuffer = 1
    sample_rate = "1KHz"
    PGA_gain = 2
    iv_gain = "POT_GAIN_300K"
    KStat.abort(ser)
    KStat.setupADC(ser, ADSbuffer, sample_rate, PGA_gain)
    KStat.setGain(ser, iv_gain)

stored_stamp = ''
if __name__ == '__main__':
    while True:
        try:
            initialize_redis()
            initialize_motor()
            initialize_KStat()
            # main loop: check for updates on root server and execute commands from front end
            while True:
                #flush local cache to get fresh copy of timestamp from server to compare
                root.flush()
                program = str(root.program)
                if program == 'hg_plater':
                    config_stamp = literal_eval(str(root.hg_plater_timestamp))
                    if config_stamp != stored_stamp:
                        if hg_plater.check_config(motor,ser):
                            stored_stamp = config_stamp
                elif program == 'single_CV':
                    config_stamp = literal_eval(str(root.single_CV_timestamp))
                    if config_stamp != stored_stamp:
                        if single_CV.check_config(motor,ser):
                            stored_stamp = config_stamp
                elif program == 'single_DPV':
                    config_stamp = literal_eval(str(root.single_DPV_timestamp))
                    if config_stamp != stored_stamp:
                        if single_DPV.check_config(motor,ser):
                            stored_stamp = config_stamp
                elif program == 'electrode_test':
                    config_stamp = literal_eval(str(root.electrode_test_timestamp))
                    if config_stamp != stored_stamp:
                        if electrode_test.check_config(motor,ser):
                            stored_stamp = config_stamp
        except Exception as e:
            print(e)
            sleep(1)
            
                
        
