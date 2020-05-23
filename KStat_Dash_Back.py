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
from kstat_interface.backend_apps.hg_au_electrode_testing import hg_au_electrode_testing
from kstat_interface.backend_apps.single_cv import single_cv
from kstat_interface.backend_apps.single_dpv import single_dpv
from kstat_interface.backend_apps.single_lsv import single_lsv
from kstat_interface.backend_apps.single_swv import single_swv
from kstat_interface import redis_config
import RPi.GPIO as GPIO
from multiprocessing import Process

# Serial address of KStat at specific USB port
KStat_path = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0'

# set control components to be enabled/disabled correctly in case program exited incorrectly before
def initialize_components():
    write_config([{'component':'purge_switch','attribute':'disabled','value':False},
                  {'component':'stirr_switch','attribute':'disabled','value':False},
                  {'component':'start_button','attribute':'disabled','value':False},
                  {'component':'stop_button','attribute':'disabled','value':True},
                  ])

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
    KStat.idle(ser,0)

stored_stamp = ''
if __name__ == '__main__':
    while True:
        try:
            initialize_redis()
            initialize_motor()
            initialize_KStat()
            initialize_components()
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
                            measurement_config=config 
                            
                            # find which program was selected and execute the corresponding script
                            if config['program_selection']['value'] == 'hg_au_electrode_plating':
                                measurement = Process(target=hg_au_electrode_plating,args=(measurement_config,motor,ser))
                            elif config['program_selection']['value'] == 'hg_au_electrode_testing':
                                measurement = Process(target=hg_au_electrode_testing,args=(measurement_config,motor,ser))
                            elif config['program_selection']['value'] == 'single_cv':
                                measurement = Process(target=single_cv,args=(measurement_config,motor,ser))
                            elif config['program_selection']['value'] == 'single_dpv':
                                measurement = Process(target=single_dpv,args=(measurement_config,motor,ser))
                            elif config['program_selection']['value'] == 'single_lsv':
                                measurement = Process(target=single_lsv,args=(measurement_config,motor,ser))
                            elif config['program_selection']['value'] == 'single_swv':
                                measurement = Process(target=single_swv,args=(measurement_config,motor,ser))
                                
                            measurement.start()
                            
                        if config['stop_button']['triggered']:
                            print('stop', config['program_selection']['value'])
                            write_config([{'component':'purge_switch','attribute':'on','value':measurement_config['purge_switch']['on']},
                                            {'component':'purge_switch','attribute':'disabled','value':False},
                                            {'component':'stirr_switch','attribute':'on','value':measurement_config['stirr_switch']['on']},
                                            {'component':'stirr_switch','attribute':'disabled','value':False},
                                            {'component':'start_button','attribute':'disabled','value':False},
                                            {'component':'stop_button','attribute':'disabled','value':True},
                                            {'component':'stop_button','attribute':'triggered','value':False},
                                            {'component':'scan_progress_label','attribute':'children','value':'Cancelled'}])
                            measurement.terminate()
                            KStat.abort(ser)
                            KStat.idle(ser,0)
                            
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            sleep(1)