from kstat_interface.backend_apps.drivers.tb6612_motor_driver import TB6612
from time import sleep, time
import kstat_interface.backend_apps.drivers.KStat_0_1_driver as KStat
from serial import Serial
from sched import scheduler
from multiprocessing import Process
from redisworks import Root
from ast import literal_eval
from kstat_interface.dash_apps.app import write_config
from kstat_interface.backend_apps.hg_au_electrode_plating import hg_au_electrode_plating
from kstat_interface import redis_config
import RPi.GPIO as GPIO
from multiprocessing import Process

# Serial address of KStat at specific USB port
KStat_path = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0'

# start redisworks server and store initial config
def initialize_redis():
    global root
    redis_host,redis_port = redis_config.get_config()
    root = Root(host=redis_host, port=redis_port, db=0)

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
            updated_timestamp=str(time())
            # main loop: check for updates on root server and execute commands from front end
            while True:
                try:
                    root.flush()
                    updates_timestamp = str(root.update_timestamp)
                    if updates_timestamp != updated_timestamp:
                        
                        updated_timestamp = updates_timestamp
                        config = literal_eval(str(root.config))
                        
                        if config['purge_switch']['on']:
                            motor.activate('A')
                        else:
                            motor.deactivate('A')
                        if config['stirr_switch']['on']:
                            motor.start('B', config['stirr_speed_slider']['value']/25)
                        else:
                            motor.start('B',0)
                            
                        if config['start_button']['triggered']:
                            print('start', config['program_selection']['value'], config['popup_measurement_id']['value'])
                            write_config([{'component':'start_button','attribute':'triggered','value':False},
                                            {'component':'stop_button','attribute':'disabled','value':False},
                                            {'component':'start_button','attribute':'disabled','value':True}])
                            if config['program_selection']['value'] == 'hg_au_electrode_plating':
                                measurement_config=config
                                measurement = Process(target=hg_au_electrode_plating,args=(measurement_config,motor,ser))
                            measurement.start()
                            
                        if config['stop_button']['triggered']:
                            print('stop', config['program_selection']['value'])
                            write_config([{'component':'stop_button','attribute':'triggered','value':False}])
                            
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            sleep(1)
            
                
        
