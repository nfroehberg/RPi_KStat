import sys, struct, time, re
from serial import Serial
import pandas as pd
import matplotlib
# for headless use
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

def mVtoDAC(mV):
    #convert milivolts to DAC indices
    return int(mV*(65536/4096)+32768)

def slopetoDAC(mV):
    #convert mV/s to DAC indices/s
    return int(mV*(65536/4096))

def DACtomV(DAC):
    #convert DAC indices to milivolts
    return (DAC-32768)*(4096/65536)

def ADCtoA(ADC, PGA_gain, iv_gain):
    #convert ADC values to current
    iv_gains = {"POT_GAIN_0":0, "POT_GAIN_100":100, "POT_GAIN_3K":3000,
                "POT_GAIN_30K":30000, "POT_GAIN_300K":300000,
                "POT_GAIN_3M":3000000, "POT_GAIN_30M":30000000,
                "POT_GAIN_100M":100000000}
    return (ADC/(PGA_gain/2))*(2/iv_gains[iv_gain]/8388607)

def ADCtomV(ADC, PGA_gain):
    #convert ADC values to voltage (for potentiometry)
    return (ADC/(PGA_gain/2))*(2000/8388607)

def sendCommand(ser, cmd, retries = 3):
    #Request to send command and confirm if received
    ser.write(bytes('!{}\r\n'.format(len(cmd)-2), encoding='ascii'))
    response = ser.readline()
    #print(response)   
    #print(len(cmd))
    if response == bytes('@ACK {}\n'.format(len(cmd)-2), encoding='ascii'):
        ser.write(cmd)
        #print(cmd)
        response = ser.readline()
        #print(response)
        if response == bytes('@RCV {}\n'.format(len(cmd)-2), encoding='ascii'):
            print("Command {} sent to KStat.".format(cmd))
        else:
            print("Sending command not successful, retrying in 1s")
            time.sleep(1)
            if retries > 0:
                return sendCommand(ser, cmd, retries = retries -1)
            else:
                print("Sending command not successful, number of retries exceeded")
    elif response == b'':
        print('KStat unresponsive, trying again')
        sendCommand(ser, cmd, retries = 3)

def idle(ser, voltage):
    #sets DStat into idle at specified voltage
    voltage = mVtoDAC(voltage)
    commands = []
    commands.append('EM')
    commands.append(str(voltage))
    commands.append('\r\n')
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))


def abort(ser):
    #abort experiment
    ser.write(b'a')
    for i in range(3):
        ser.readline()

def readSettings(ser):
    #Reads EEPROM settings and returns values as a dictionary
    sendCommand(ser, b"SR\r\n")
    for i in range(18):
        line = ser.readline()
        if i == 15:
            values = line.strip()[1:].split(b':')

            D = {}
            for c in values:
                k,v = c.decode().split('.')
                v = int(v)
                D[k] = v
    return D

def writeSettings(ser, max5443_offset = 0, tcs_enabled = 1, tcs_clear_threshold = 10000,
                  r100_trim = 0, r3k_trim = 0, r30k_trim = 0, r300k_trim = 0, r3M_trim = 0,
                  r30M_trim = 0, r100M_trim = 0, eis_cal1 = 3000, eis_cal2 = 3000000,
                  dac_units_true = 1):
    #Change EEPROM settings, all values that are not specified will be set to default
    #execute with no parameters (except ser) to reset all to default
    commands = []
    commands.append('SW')
    commands.append(str(max5443_offset))
    commands.append(str(tcs_enabled))
    commands.append(str(tcs_clear_threshold))
    commands.append(str(r100_trim))
    commands.append(str(r3k_trim))
    commands.append(str(r30k_trim))
    commands.append(str(r300k_trim))
    commands.append(str(r3M_trim))
    commands.append(str(r30M_trim))
    commands.append(str(r100M_trim))
    commands.append(str(eis_cal1))
    commands.append(str(eis_cal2))
    commands.append(str(dac_units_true))
    commands.append('\r\n')
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))
    for i in range(2):
        ser.readline()
             
    
def setupADC(ser, ADSbuffer, Samplingrate, PGA_gain):
    #Change ADC settings
    #ADS Buffer = [0,1]
    #PGA_gain = [1,2,4,8,16,32,64]
    #Samplingrate = ["2.5Hz", "5Hz", "10Hz", "15Hz", "25Hz", "30Hz", "50Hz",
    #               "60Hz", "100Hz", "500Hz", "1KHz", "2KHz", "3.75KHz", "7.5KHz", "15KHz",
    #               "30KHz"]
    commands = []
    Samplingrates = {"2.5Hz":"3", "5Hz":"13", "10Hz":"23", "15Hz":"33",
                     "25Hz":"43", "30Hz":"53", "50Hz":"63", "60Hz":"72",
                     "100Hz":"82", "500Hz":"92", "1KHz":"A1", "2KHz":"B0",
                     "3.75KHz":"C0", "7.5KHz":"D0", "15KHz":"E0", "30KHz":"E0"}
    Samplingrate = Samplingrates[Samplingrate]
    commands.append('EA')
    commands.append(str(PGA_gain))
    commands.append(str(Samplingrate))
    commands.append(str(ADSbuffer))
    commands.append('\r\n')

    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))

    for i in range(3):
        response = ser.readline()
    if response == b'@DONE\n':
        print("ADC settings updated")
    else:
        print("Setting ADC unsuccessful")

def setGain(ser, gain):
    #Change gain of the transimpedance amplifier
    #gain = ["POT_GAIN_0", "POT_GAIN_100", "POT_GAIN_3K", "POT_GAIN_30K",
    #       "POT_GAIN_300K", "POT_GAIN_3M", "POT_GAIN_30M", "POT_GAIN_100M"]
    gains = {"POT_GAIN_0":0, "POT_GAIN_100":1, "POT_GAIN_3K":2, "POT_GAIN_30K":3,
             "POT_GAIN_300K":4, "POT_GAIN_3M":5, "POT_GAIN_30M":6,
             "POT_GAIN_100M":7}
    gain = gains[gain]
    commands = []
    commands.append('EG')
    commands.append(str(gain))
    commands.append('\r\n')

    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))

    for i in range(4):
        response = ser.readline()
        if i == 2:
            gain = response
    if response == b'@DONE\n':
        print("Gain settings updated")
        print(gain)
    else:
        print("Setting gain unsuccessful")


def setPlotRange(start, v1, v2):
    #Function to determine range for plotting voltammetric data depending on scan direction
    if v1 < start:
        x1 = DACtomV(v1)
        if v2 > start:
            x2 = DACtomV(v2)
        else:
            x2 = DACtomV(start)
    elif v2 < start:
        x1 = DACtomV(v2)
        x2 = DACtomV(v1)
    else:
        x1 = DACtomV(start)
        x2 = DACtomV(v1)
    return x1, x2


def potentiometry(ser, PGA_gain, measurement_time = 0, mode = 1):
    #function for potentiometry experiment.
    #sampling rate is forced to 10 Hz because line by line readout is required for potentiometry (fast sampling can max out the serial buffer)
    #measurement time in s, if 0 will run until abort signal
    #Mode: 0 for OCP (WE is connected)/1 for potentiometry (WE input disconnected)
    setupADC(ser, ADSbuffer = 1, Samplingrate = "5Hz", PGA_gain = PGA_gain)

    commands = []
    commands.append('EP')
    commands.append(str(measurement_time))
    commands.append(str(mode))
    commands.append('\n')
    
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))

    return catchPotentiometry(ser, PGA_gain)
    
def catchPotentiometry(ser, PGA_gain):
    i = 0
    voltage = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    t = ["0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0","0:0"]
    pH = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    
    while True:
        try:
            line = ser.readline()
            if line == b'@DONE\n':
                print('Experiment complete')
                break
            elif line == b'B\n':
                pass
            else:
                try:
                    s, ms, v = struct.unpack('<HHix', line)
                    v = ADCtomV(v, PGA_gain)
                    voltage.append(v)
                    pH.append(0.0169*v+6.9097)
                    t.append(float("{}.{}".format(s,ms)))
                    plt.clf()
                    plt.xlabel('t [s]')
                    plt.ylabel('U [mV]')
                    plt.plot(t [-100:-1],voltage[-100:-1])
                    plt.draw()
                    plt.pause(0.00000001)
                except:
                    pass
                    #print("Could not read line:\n{}".format(line))
        except KeyboardInterrupt:
            abort(ser)
                

def differentialPulseVoltammetry(ser, PGA_gain, iv_gain, t_preconditioning1,
                                 t_preconditioning2, v_preconditioning1, v_preconditioning2,
                                 start, stop, step_size, pulse_height, period, width, sample_rate,
                                 file='DPV', comment='', plotting=False):
    #Run differnetial pulse voltammetry experiment and return results
    #PGA_gain = [1,2,4,8,16,32,64]
    #iv_gain = ["POT_GAIN_0", "POT_GAIN_100", "POT_GAIN_3K", "POT_GAIN_30K",
    #       "POT_GAIN_300K", "POT_GAIN_3M", "POT_GAIN_30M", "POT_GAIN_100M"]
    #t_preconditioning1, t_preconditioning2 = seconds
    #v_preconditioning1, v_preconditioning1, start, stop = DAC steps (absolute)
    #step_size, pulse_height = DAC steps (relative)
    """#period, width = ??????????"""

    #writing parameters to file:
    params = ("Differential Pulse Voltammetry Experiment\nComment =\t\t{}\nLocaltime =\t\t"+\
              "{}\nUTC =\t\t\t{}\nTimestamp =\t\t{}\nParameters:\nSamplerate =\t\t{}\nt_preconditioning1 =\t{} s"+\
              "\nt_preconditioning2 =\t{} s\nv_preconditioning1 =\t{} mV\n"+\
              "v_preconditioning2 =\t{} mV\nstart =\t\t\t{} mV\nstop =\t\t\t{} mV\n"+\
              "step_size =\t\t{} mV\npulse_height =\t\t{} mV\nperiod =\t\t{} ms\nwidth "+\
              "=\t\t\t{} ms").format(comment, datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             str(time.time()),sample_rate, str(t_preconditioning1), str(t_preconditioning2),
                             str(v_preconditioning1), str(v_preconditioning2),
                             str(start), str(stop), str(step_size), str(pulse_height),
                             str(period), str(width))
    f = open((file+'-parameters.txt'), 'w')
    f.write(params)
    f.close()
    
    v_preconditioning1 = mVtoDAC(v_preconditioning1)
    v_preconditioning2 = mVtoDAC(v_preconditioning2)
    start = mVtoDAC(start)
    stop = mVtoDAC(stop)
    step_size = slopetoDAC(step_size)
    pulse_height = slopetoDAC(pulse_height)
    commands = []
    commands.append('ED')
    commands.append(str(t_preconditioning1))
    commands.append(str(t_preconditioning2))
    commands.append(str(v_preconditioning1))
    commands.append(str(v_preconditioning2))
    commands.append(str(start))
    commands.append(str(stop))
    commands.append(str(step_size))
    commands.append(str(pulse_height))
    commands.append(str(period))
    commands.append(str(width))
    commands.append('\n')
    
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))
    
    return catchSquarewaveVoltammetry(ser, PGA_gain, iv_gain, file, plotting)


def squarewaveVoltammetry(ser, PGA_gain, iv_gain, t_preconditioning1,
                          t_preconditioning2, v_preconditioning1, v_preconditioning2,
                          start, stop, step_size, pulse_height, frequency, scans, sample_rate,
                          file='SWV', comment='', plotting=False):
    #Run squarewave voltammetry experiment and return results
    #PGA_gain = [1,2,4,8,16,32,64]
    #iv_gain = ["POT_GAIN_0", "POT_GAIN_100", "POT_GAIN_3K", "POT_GAIN_30K",
    #       "POT_GAIN_300K", "POT_GAIN_3M", "POT_GAIN_30M", "POT_GAIN_100M"]
    #t_preconditioning1, t_preconditioning2 = seconds
    #v_preconditioning1, v_preconditioning1, start, stop = DAC steps (absolute)
    #step_size, pulse_height = DAC steps (relative)
    #frequency = Hz

    #writing parameters to file:
    params = ("Squarewave Voltammetry Experiment\nComment =\t\t{}\nLocaltime =\t\t"+\
              "{}\nUTC =\t\t\t{}\nTimestamp =\t\t{}\nParameters:\nSamplerate =\t\t{}\nt_preconditioning1 =\t{} s"+\
              "\nt_preconditioning2 =\t{} s\nv_preconditioning1 =\t{} mV\n"+\
              "v_preconditioning2 =\t{} mV\nstart =\t\t\t{} mV\nstop =\t\t\t{} mV\n"+\
              "step_size =\t\t{} mV\npulse_height =\t\t{} mV\nfrequency =\t\t{} Hz\nn_scans"+\
              "=\t\t{}").format(comment, datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             str(time.time()),sample_rate, str(t_preconditioning1), str(t_preconditioning2),
                             str(v_preconditioning1), str(v_preconditioning2),
                             str(start), str(stop), str(step_size), str(pulse_height),
                             str(frequency), str(scans))
    f = open((file+'-parameters.txt'), 'w')
    f.write(params)
    f.close()

    v_preconditioning1 = mVtoDAC(v_preconditioning1)
    v_preconditioning2 = mVtoDAC(v_preconditioning2)
    start = mVtoDAC(start)
    stop = mVtoDAC(stop)
    step_size = slopetoDAC(step_size)
    pulse_height = slopetoDAC(pulse_height)
    commands = []
    commands.append('ES')
    commands.append(str(t_preconditioning1))
    commands.append(str(t_preconditioning2))
    commands.append(str(v_preconditioning1))
    commands.append(str(v_preconditioning2))
    commands.append(str(start))
    commands.append(str(stop))
    commands.append(str(step_size))
    commands.append(str(pulse_height))
    commands.append(str(frequency))
    commands.append(str(scans))
    commands.append('\r\n')
    
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))
    
    return catchSquarewaveVoltammetry(ser, PGA_gain, iv_gain, file, plotting)

def catchSquarewaveVoltammetry(ser, PGA_gain, iv_gain, file, plotting):
    #save and return lines produced by squarewave voltammetry experiment

    response = bytearray()   
    while True:
        line = ser.read(2500)
        response += line
        if b'@DONE\n' in line:
            print('Data received')
            break
        
    #pattern of data line:
    pattern = re.compile(b'(B\n[\s\S]{10}\n*)|(S\n)|(@DONE\n)')
    lines = []
    for x in re.finditer(pattern, response):
        lines.append(x.group())
    scans = [[]]
    index = 0
    for element in lines:
        #detecting scans and initializing lists for data:
        if element == b'S\n':
            index += 1
            scans.append([])
        else:
            scans[index].append(element)
    n_scans = index
    
    if not b'@DONE\n' in scans[-1]:
        return "Error: Data transmission failed"
    else:
        result = []
        for i in range(len(scans)):
            scan = scans[i]
            result.append({})
            potential = []
            forwardcurrent = []
            backwardcurrent = []  
            raw = []
            for element in scan:
                #DStat sometimes generates bad data points, excluding current range -16 to +16:
                #if (re.findall(re.compile(b'[\xf0-\xff]\xff\xff\xff\n'), element) == \
                #re.findall(re.compile(b'[\x00-\x0f]\x00\x00\x00\n'), element) == []):
                try:
                    v, fi1, fi2 = struct.unpack('<xxHiix', element)
                    potential.append(DACtomV(v))
                    forwardcurrent.append(ADCtoA(fi1, PGA_gain, iv_gain))
                    backwardcurrent.append(ADCtoA(fi2, PGA_gain, iv_gain))
                except:
                    pass
            potential = potential[3:] # first datapoints are usually faulty
            forwardcurrent = forwardcurrent[3:]
            backwardcurrent = backwardcurrent[3:]
            
            #subtract backward from forward current
            fbcurrent = []
            for j in range(len(forwardcurrent)):
                fbcurrent.append(forwardcurrent[j]-backwardcurrent[j])
                
            result[i]['potential'] = potential
            result[i]['forwardcurrent'] = forwardcurrent
            result[i]['backwardcurrent'] = backwardcurrent
            result[i]['fbcurrent'] = fbcurrent

            #writing data to file
            if n_scans > 1:
                filename = file + '-scan' + str(i)
            else:
                filename = file
                
            out = pd.DataFrame(result[i])
            out.to_csv((filename+'.csv'), index = False)
            if plotting:
                fig = plt.figure(figsize=(6,4))
                plt.plot(result[i]['potential'], result[i]['fbcurrent'], 'b-')
                plt.gca().invert_xaxis()
                plt.gca().invert_yaxis()
                plt.xlabel('Potential [mV]')
                plt.ylabel('Forward - Backward Current [A]')
                plt.title(filename)
                fig.savefig((filename+'.png'), dpi=150)
                
                plt.clf()
                               
                plt.close()
    
        print('Scans: ', n_scans + 1)
        print("Processing complete")
        return result



def linearSweepVoltammetry(ser, PGA_gain, iv_gain, t_preconditioning1, t_preconditioning2,
                           v_preconditioning1, v_preconditioning2, start, stop, slope, sample_rate,
                           file='LSV', comment='', plotting=False):
    #Run linear sweep voltammetry experiment and return results
    #PGA_gain = [1,2,4,8,16,32,64]
    #iv_gain = ["POT_GAIN_0", "POT_GAIN_100", "POT_GAIN_3K", "POT_GAIN_30K",
    #       "POT_GAIN_300K", "POT_GAIN_3M", "POT_GAIN_30M", "POT_GAIN_100M"]
    #t_preconditioning1, t_preconditioning2 = seconds
    #v_preconditioning1, v_preconditioning1, start, stop = DAC steps (absolute)
    #slope = DAC steps (relative)

    #writing parameters to file:
    params = ("Linear Sweep Voltammetry Experiment\nComment =\t\t{}\nLocaltime =\t\t"+\
              "{}\nUTC =\t\t\t{}\nTimestamp =\t\t{}\nParameters:\nSamplerate =\t\t{}\nt_preconditioning1 =\t{} s"+\
              "\nt_preconditioning2 =\t{} s\nv_preconditioning1 =\t{} mV\n"+\
              "v_preconditioning2 =\t{} mV\nstart =\t\t\t{} mV\nstop =\t\t\t{} mV\n"+\
              "slope =\t\t\t{} mV/s").format(comment, datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             str(time.time()), sample_rate, str(t_preconditioning1), str(t_preconditioning2),
                                   str(v_preconditioning1), str(v_preconditioning2),
                                    str(start), str(stop), str(slope))
    f = open((file+'-parameters.txt'), 'w')
    f.write(params)
    f.close()
    
    v_preconditioning1 = mVtoDAC(v_preconditioning1)
    v_preconditioning2 = mVtoDAC(v_preconditioning2)
    start = mVtoDAC(start)
    stop = mVtoDAC(stop)
    slope = slopetoDAC(slope)
    commands = []
    commands.append("EL")
    commands.append(str(t_preconditioning1))
    commands.append(str(t_preconditioning2))
    commands.append(str(v_preconditioning1))
    commands.append(str(v_preconditioning2))
    commands.append(str(start))
    commands.append(str(stop))
    commands.append(str(slope))
    commands.append('\r\n')
    
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))

    #Data are returned in same format as for cyclic voltammetry
    return catchCyclicVoltammetry(ser, PGA_gain, iv_gain, file, plotting)


def cyclicVoltammetry(ser, PGA_gain, iv_gain, t_preconditioning1, t_preconditioning2,
                      v_preconditioning1, v_preconditioning2, v1, v2,
                      start, n_scans, slope, sample_rate, file = 'CV', comment='', plotting=False):
    #Run cyclic voltammetry experiment and return results
    #PGA_gain = [1,2,4,8,16,32,64]
    #iv_gain = ["POT_GAIN_0", "POT_GAIN_100", "POT_GAIN_3K", "POT_GAIN_30K",
    #       "POT_GAIN_300K", "POT_GAIN_3M", "POT_GAIN_30M", "POT_GAIN_100M"]
    #t_preconditioning1, t_preconditioning2 = seconds
    #v_preconditioning1, v_preconditioning1, v1, v2, start = DAC steps (absolute)
    #slope = DAC steps (relative)
    #writing parameters to file:
    params = ("Cyclic Voltammetry Experiment\nComment =\t\t{}\nLocaltime =\t\t"+\
              "{}\nUTC =\t\t\t{}\nTimestamp =\t\t{}\nParameters:\nSamplerate =\t\t{}\nt_preconditioning1 =\t{} s"+\
              "\nt_preconditioning2 =\t{} s\nv_preconditioning1 =\t{} mV\n"+\
              "v_preconditioning2 =\t{} mV\nv1 =\t\t\t{} mV\nv2 =\t\t\t{} mV\nstart =\t\t\t"+\
              "{} mV\nn_scans =\t\t{}\n"+\
              "slope =\t\t\t{} mV/s").format(comment, datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                             str(time.time()),sample_rate, str(t_preconditioning1), str(t_preconditioning2),
                                   str(v_preconditioning1), str(v_preconditioning2),
                                   str(v1), str(v2), str(start), str(n_scans), str(slope))
    f = open((file+'-parameters.txt'), 'w')
    f.write(params)
    f.close()
    v_preconditioning1 = mVtoDAC(v_preconditioning1)
    v_preconditioning2 = mVtoDAC(v_preconditioning2)
    start = mVtoDAC(start)
    v1 = mVtoDAC(v1)
    v2 = mVtoDAC(v2)
    slope = slopetoDAC(slope)
    commands = []
    commands.append("EC")
    commands.append(str(t_preconditioning1))
    commands.append(str(t_preconditioning2))
    commands.append(str(v_preconditioning1))
    commands.append(str(v_preconditioning2))
    commands.append(str(v1))
    commands.append(str(v2))
    commands.append(str(start))
    commands.append(str(n_scans))
    commands.append(str(slope))
    commands.append('\r\n')
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))
    
    return catchCyclicVoltammetry(ser, PGA_gain, iv_gain, file, plotting, n_scans)



def catchCyclicVoltammetry(ser, PGA_gain, iv_gain, file, plotting, n_scans=1):
    #save and return lines produced by cyclic voltammetry experiment

    response = bytearray()   
    while True:
        line = ser.read(2500)
        #print(line)
        response += line
        if b'@DONE\n' in line:
            print('Data received')
            break
    #print(response)
        
    #pattern of data line:
    pattern = re.compile(b'(B\n[\s\S]{6}\n*)|(S\n)|(@DONE\n)')
    lines = []
    for x in re.finditer(pattern, response):
        lines.append(x.group())
    scans = [[]]
    index = 0
    for element in lines:
        #detecting scans and initializing lists for data:
        if element == b'S\n':
            index += 1
            scans.append([])
        else:
            scans[index].append(element)
    
    #print(scans)
    if not b'@DONE\n' in scans[-1]:
        print("Error: Data transmission failed")
        return "Error: Data transmission failed"
    else:
        result = []
        for i in range(len(scans)-1):
            scan = scans[i]
            result.append({})
            potential = []
            current = []
            raw = []
            for element in scan:
                #DStat sometimes generates bad data points, excluding current range -16 to +16:
                if (re.findall(re.compile(b'[\xf0-\xff]\xff\xff\xff\n'), element) == \
                re.findall(re.compile(b'[\x00-\x0f]\x00\x00\x00\n'), element) == []):
                    v, fi = struct.unpack('<xxHix', element)
                    potential.append(DACtomV(v))
                    current.append(ADCtoA(fi, PGA_gain, iv_gain))
            potential = potential[3:] # first datapoints are usually faulty
            current = current[3:]
            result[i]['potential'] = potential
            result[i]['current'] = current

            #writing data to file
            if n_scans > 1:
                filename = file + '-scan' + str(i)
            else:
                filename = file
            out = pd.DataFrame(result[i])
            out.to_csv((filename+'.csv'), index = False)
            if plotting:
                fig = plt.figure(figsize=(6,4))
                plt.plot(result[i]['potential'], result[i]['current'], 'b-')
                plt.gca().invert_xaxis()
                plt.gca().invert_yaxis()
                plt.xlabel('Potential [mV]')
                plt.ylabel('Current [A]')
                plt.title(filename)
                fig.savefig((filename+'.png'), dpi=150)
                plt.close()

    
        print('Scans: ', len(result))
        print("processing complete")
        return result
