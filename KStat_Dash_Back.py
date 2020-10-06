from kstat_interface.backend_apps.drivers.tb6612_motor_driver import TB6612
from kstat_interface.backend_apps.drivers.pololu_tic_driver import TicUSB
from time import sleep, time
import kstat_interface.backend_apps.drivers.KStat_0_1_driver as KStat
from serial import Serial
from sched import scheduler
from multiprocessing import Process
from redisworks import Root
from ast import literal_eval
from kstat_interface.dash_apps.app import write_config, controls_disabled
from kstat_interface.backend_apps.hg_au_electrode_plating import hg_au_electrode_plating
from kstat_interface.backend_apps.hg_au_electrode_testing import hg_au_electrode_testing
from kstat_interface.backend_apps.single_cv import single_cv
from kstat_interface.backend_apps.single_dpv import single_dpv
from kstat_interface.backend_apps.single_lsv import single_lsv
from kstat_interface.backend_apps.single_swv import single_swv
from kstat_interface.backend_apps.profiler_measurement import profiler_measurement
from kstat_interface.backend_apps.profiler_movement import profiler_home, profiler_move_step
from kstat_interface import redis_config
import RPi.GPIO as GPIO
from multiprocessing import Process
from glob import glob
#from serial import Serial
from smbus2 import SMBus

# set control components to be enabled/disabled correctly in case program exited incorrectly before
def initialize_components():
    write_config([{'component':'purge_switch','attribute':'disabled','value':False},
                  {'component':'stirr_switch','attribute':'disabled','value':False},
                  {'component':'start_button','attribute':'disabled','value':False},
                  {'component':'home_button','attribute':'disabled','value':False},
                  {'component':'move_step_button','attribute':'disabled','value':False},
                  {'component':'upload_button','attribute':'disabled','value':False},
                  {'component':'download_button','attribute':'disabled','value':False},
                  {'component':'change_directory_button','attribute':'disabled','value':False},
                  {'component':'stop_button','attribute':'disabled','value':True},
                  {'component':'stop_button','attribute':'triggered','value':False},
                  {'component':'start_button','attribute':'triggered','value':False},
                  {'component':'move_step_button','attribute':'triggered','value':False},
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
    devices = glob('/dev/serial/by-id/*')
    KStat_port = ''
    for port in devices:
        if 'DStat' in port:
            KStat_port = port
            global ser
            ser = Serial(KStat_port, 9600, timeout = 1)
            ADSbuffer = 1
            sample_rate = "1KHz"
            PGA_gain = 2
            iv_gain = "POT_GAIN_300K"
            KStat.abort(ser)
            KStat.setupADC(ser, ADSbuffer, sample_rate, PGA_gain)
            KStat.setGain(ser, iv_gain)
            KStat.idle(ser,0)
            break
    if KStat_port == '':
        print('No KStat connected')

def initialize_profiler():
    global profiler, mm
    # calibrate speed
    step_mode = 5
    screw_pitch = 4 # mm
    steps_per_rotation = 200 * (2**step_mode)
    mm = steps_per_rotation/screw_pitch
    
    config = literal_eval(str(root.config))
    max_speed = int(config['max_speed_input']['value'] * mm * 10000)
    max_acceleration = int(config['max_acceleration_input']['value'] * mm * 100)
    try:
        #port = Serial("/dev/serial0", 9600, timeout=0.1, write_timeout=0.1)
        #profiler = TicSerial(port,limits=True)
        profiler = TicUSB(limits=True)
        profiler.reset()
        profiler.energize()
        profiler.halt_and_set_position()
        profiler.set_step_mode(step_mode)
        profiler.set_max_speed(max_speed)
        profiler.set_max_acceleration(max_acceleration)
        profiler.set_max_deceleration(max_acceleration)
        profiler.set_current_limit(124)
    except Exception as e:
        print('Could not initialize profiler', e)
        profiler = 9

stored_stamp = ''
if __name__ == '__main__':
    while True:
        try:
            initialize_redis()
            initialize_motor()
            initialize_KStat()
            initialize_profiler()
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
                            elif config['program_selection']['value'] == 'profiler_cv':
                                measurement = Process(target=profiler_measurement,args=('cv',measurement_config,motor,ser,profiler,mm))
                            elif config['program_selection']['value'] == 'profiler_lsv':
                                measurement = Process(target=profiler_measurement,args=('lsv',measurement_config,motor,ser,profiler,mm))
                            elif config['program_selection']['value'] == 'profiler_dpv':
                                measurement = Process(target=profiler_measurement,args=('dpv',measurement_config,motor,ser,profiler,mm))
                            elif config['program_selection']['value'] == 'profiler_swv':
                                measurement = Process(target=profiler_measurement,args=('swv',measurement_config,motor,ser,profiler,mm))
                                
                            measurement.start()
                            
                        if config['stop_button']['triggered']:
                            print('stop', config['program_selection']['value'])
                            controls_disabled(False)
                            write_config([{'component':'purge_switch','attribute':'on','value':measurement_config['purge_switch']['on']},
                                            {'component':'stirr_switch','attribute':'on','value':measurement_config['stirr_switch']['on']},
                                            {'component':'stop_button','attribute':'triggered','value':False},
                                            {'component':'scan_progress_label','attribute':'children','value':'Cancelled'}])
                            measurement.terminate()
                            KStat.abort(ser)
                            KStat.idle(ser,0)
                            
                        if config['home_button']['triggered']:
                            write_config([{'component':'home_button','attribute':'triggered','value':False},
                                            {'component':'start_button','attribute':'disabled','value':True},
                                            {'component':'stop_button','attribute':'disabled','value':True},
                                            {'component':'home_button','attribute':'disabled','value':True},
                                            {'component':'move_step_button','attribute':'disabled','value':True},])
                            profiler_move = Process(target=profiler_home,args=(config,profiler,mm))
                            profiler_move.start()
                        if config['move_step_button']['triggered']:
                            write_config([{'component':'move_step_button','attribute':'triggered','value':False},
                                            {'component':'start_button','attribute':'disabled','value':True},
                                            {'component':'stop_button','attribute':'disabled','value':True},
                                            {'component':'home_button','attribute':'disabled','value':True},
                                            {'component':'move_step_button','attribute':'disabled','value':True},])
                            profiler_move = Process(target=profiler_move_step,args=(config,profiler,mm))
                            profiler_move.start()
                        
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            sleep(1)