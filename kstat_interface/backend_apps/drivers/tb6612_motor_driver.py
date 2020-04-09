import time
import RPi.GPIO as GPIO
# Raspberry Pi driver for the Adafruit TB6612 Dual Motor Driver
# For wiring diagram see https://howchoo.com/g/mjg5ytzmnjh/controlling-dc-motors-using-your-raspberry-pi
# Nico Fröhberg, 2019
# https://github.com/nfroehberg
# nico.froehberg@gmx.de


# Class for the Adafruit TB6612 Dual Motor Driver
class TB6612():

    def __init__(self, dirA = 'clockwise', PWMA = 7, AIN2 = 11, AIN1 = 12,
                 STBY = 13, BIN1 = 15, BIN2 = 16, PWMB = 18, dirB = 'clockwise'):
        """
        initilaize variables for the GPIO pins on the Raspberry Pi connected to the TB6612 input
        """
        
        GPIO.setmode(GPIO.BOARD)
        self.dirA = dirA
        self.PWMA = PWMA
        GPIO.setup(PWMA, GPIO.OUT)
        self.pA = GPIO.PWM(PWMA, 100)
        self.AIN2 = AIN2
        GPIO.setup(AIN2, GPIO.OUT)
        self.AIN1 = AIN1
        GPIO.setup(AIN1, GPIO.OUT)
        self.STBY = STBY
        GPIO.setup(STBY, GPIO.OUT)
        self.BIN1 = BIN1
        GPIO.setup(BIN1, GPIO.OUT)
        self.BIN2 = BIN2
        GPIO.setup(BIN2, GPIO.OUT)
        self.PWMB = PWMB
        GPIO.setup(PWMB, GPIO.OUT)
        self.dirB = dirB
        self.pB = GPIO.PWM(PWMB, 100)
        
        self.set_dir('A', dirA)
        self.set_dir('B', dirB)

    def __del__(self):
        GPIO.cleanup() 

    def standby(self, stby = True):
        """
        activate/deactivate standby signal
        """
        
        if stby:
            GPIO.output(self.STBY, GPIO.LOW)
        else:
            GPIO.output(self.STBY, GPIO.HIGH)

    def set_dir(self, motor, dir_motor = 'clockwise'):
        """
        select direction of motor
        """
        
        if motor == 'A':
            if dir_motor == 'clockwise':
                self.dirA = 'clockwise'
                GPIO.output(self.AIN1, GPIO.HIGH)
                GPIO.output(self.AIN2, GPIO.LOW)
            elif dir_motor == 'counterclockwise':
                self.dirA = 'counterclockwise'
                GPIO.output(self.AIN1, GPIO.LOW)
                GPIO.output(self.AIN2, GPIO.HIGH)
            else:
                print("Direction specified incorrectly. Select 'clockwise' or 'counterclockwise'.")
        elif motor == 'B':
            if dir_motor == 'clockwise':
                self.dirB = 'clockwise'
                GPIO.output(self.BIN1, GPIO.HIGH)
                GPIO.output(self.BIN2, GPIO.LOW)
            elif dir_motor == 'counterclockwise':
                self.dirB = 'counterclockwise'
                GPIO.output(self.BIN1, GPIO.LOW)
                GPIO.output(self.BIN2, GPIO.HIGH)
            else:
                print("Direction specified incorrectly. Select 'clockwise' or 'counterclockwise'.")
        else:
            print("Motor specified incorrectly. Select 'A' or 'B'.")
            
    def switch_dir(self, motor):
        """
        reverse direction of motor
        """
        
        if motor == 'A':
            if self.dirA == 'counterclockwise':
                self.dirA = 'clockwise'
                GPIO.output(self.AIN1, GPIO.HIGH)
                GPIO.output(self.AIN2, GPIO.LOW)
            elif self.dirA == 'clockwise':
                self.dirA = 'counterclockwise'
                GPIO.output(self.AIN1, GPIO.LOW)
                GPIO.output(self.AIN2, GPIO.HIGH)
                
        elif motor == 'B':
            if self.dirB == 'counterclockwise':
                self.dirB = 'clockwise'
                GPIO.output(self.BIN1, GPIO.HIGH)
                GPIO.output(self.BIN2, GPIO.LOW)
            elif self.dirB == 'clockwise':
                self.dirB = 'counterclockwise'
                GPIO.output(self.BIN1, GPIO.LOW)
                GPIO.output(self.BIN2, GPIO.HIGH)

        else:
            print("Motor specified incorrectly. Select 'A' or 'B'.")

    def start(self, motor, speed = 100):
        """
        start motor using pulse width modulation for speed control
        """
        
        if motor == 'A':
            self.pA.start(speed)
        elif motor == 'B':
            self.pB.start(speed)
        else:
            print("Motor specified incorrectly. Select 'A' or 'B'.")

    def set_speed(self, motor, speed):
        """
        change motor speed using pulse width modulation
        """
        
        if motor == 'A':
            try:
                speed = int(speed)
            except:
                print("Speed specified incorrectly, slect a number between 1 and 100.")
            self.pA.ChangeDutyCycle(speed)
            
        elif motor == 'B':
            try:
                speed = int(speed)
            except:
                print("Speed specified incorrectly, slect a number between 1 and 100.")
            self.pB.ChangeDutyCycle(speed)

        else:
            print("Motor specified incorrectly. Select 'A' or 'B'.")

    def activate(self, motor):
        """
        start motor at full speed
        """
        
        if motor == 'A':
            GPIO.output (self.PWMA, GPIO.HIGH)
        elif motor == 'B':
            GPIO.output (self.PWMB, GPIO.HIGH)

        else:
            print("Motor specified incorrectly. Select 'A' or 'B'.")

    def deactivate(self, motor):
        """
        stop motor
        """
        
        if motor == 'A':
            GPIO.output (self.PWMA, GPIO.LOW)
        elif motor == 'B':
            GPIO.output (self.PWMB, GPIO.LOW)

        else:
            print("Motor specified incorrectly. Select 'A' or 'B'.")
            
            
if __name__=="__main__":
    
    motor = TB6612(dirA = 'clockwise', PWMA = 7, AIN2 = 11, AIN1 = 12, STBY = 13, BIN1 = 15,
                   BIN2 = 16, PWMB = 18, dirB = 'clockwise')
    motor.standby(False)
    motor.start('B', 50)
    for i in range(500):
        motor.activate('A')
        time.sleep(1)
        motor.deactivate('A')
        time.sleep(1)
    time.sleep(600)
