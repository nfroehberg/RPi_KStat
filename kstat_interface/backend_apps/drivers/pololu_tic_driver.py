# Driver for Pololu Tic T825 stepper motor driver through serial
# Nico Froehberg nico.froehberg@gmx.de
# Adapted from https://www.pololu.com/docs/0J71/12.7
# For command documentation see https://www.pololu.com/docs/0J71/8

# Uses the pySerial library to send and receive data from a Tic.
#
# NOTE: The Tic's control mode must be "Serial / I2C / USB".
# NOTE: You will need to change the "port_name =" line below to specify the 
#   right serial port.
 
import time
import RPi.GPIO as GPIO 

# Converts value to bytes of 32bit commands.
# Use as *write32(p) (uses elements of list as individual arguments rather than
# entire list as one)
def write32(p):
    m = [((p >>  7) & 1) | ((p >> 14) & 2) | ((p >> 21) & 4) | ((p >> 28) & 8),
         p >> 0 & 0x7F,
         p >> 8 & 0x7F,
         p >> 16 & 0x7F,
         p >> 24 & 0x7F]
    return m


  
class TicSerial(object):
  def __init__(self, port, device_number=None, limits=False, top_limit_gpio=19, bottom_limit_gpio=23):
    self.port = port
    self.device_number = device_number
    self.limits = limits 
    if self.limits:
        # initiate limit switches and check if either is active
        self.top_limit_gpio = top_limit_gpio
        self.bottom_limit_gpio = bottom_limit_gpio
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([self.top_limit_gpio, self.bottom_limit_gpio], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        limit = self.check_limit()
        if limit == "top":
            self.top = True
            self.bottom = False
        elif limit == "bottom":
            self.bottom = True
            self.top = False
        else:
            self.top = False
            self.bottom = False
            
    # limit switches deactivate profiler according to direction of movement
    # stepper driver produces noise in wires going to the switches, check 3 times to make sure it's a real signal
    # switches are normally closed for safety (broken connection deactivates profiler)
  def check_limit(self):
        if GPIO.input(self.top_limit_gpio):
                if GPIO.input(self.top_limit_gpio):
                    if GPIO.input(self.top_limit_gpio):
                        return "top"
        if GPIO.input(self.bottom_limit_gpio): 
            if GPIO.input(self.bottom_limit_gpio):
                if GPIO.input(self.bottom_limit_gpio):
                    return "bottom"
        return None 
        
  def send_command(self, cmd, *data_bytes):
    if self.device_number == None:
      header = [cmd]  # Compact protocol
    else:
      header = [0xAA, device_number, cmd & 0x7F]  # Pololu protocol
    self.port.write(header + list(data_bytes))
 
  # Sets the target position.
  def set_target_position(self, target):
    self.send_command(0xE0, *write32(target))
 
  # Sets the target velocity of the Tic, in microsteps per 10,000 seconds.
  def set_target_velocity(self, targetv):
    self.send_command(0xE3, *write32(targetv))
 
  # Gets one or more variables from the Tic.
  def get_variables(self, offset, length):
    self.send_command(0xA1, offset, length)
    result = self.port.read(length)
    if len(result) != length:
      raise RuntimeError("Expected to read {} bytes, got {}."
        .format(length, len(result)))
    return bytearray(result)
 
  # Gets the "Current position" variable from the Tic.
  def get_current_position(self):
    try:
        b = self.get_variables(0x22, 4)
        position = b[0] + (b[1] << 8) + (b[2] << 16) + (b[3] << 24)
        if position >= (1 << 31):
          position -= (1 << 32)
        return position
    except:
        print('Could not get current position, trying again.')
        self.exit_safe_start()
        return self.get_current_position()
 
  # Reads a block of data from the Tic’s settings (stored in non-volatile memory).
  def get_setting(self, offset, length):
    self.send_command(0xA8, offset, length)
    result = self.port.read(length)
    if len(result) != length:
      raise RuntimeError("Expected to read {} bytes, got {}."
        .format(length, len(result)))
    return bytearray(result)
 
  # Gets one or more variables from the Tic.
  # Also clears the “Errors occurred” variable at the same time.
  def get_variables_and_clear_errors(self, offset, length):
    self.send_command(0xA2, offset, length)
    result = self.port.read(length)
    if len(result) != length:
      raise RuntimeError("Expected to read {} bytes, got {}."
        .format(length, len(result)))
    return bytearray(result)
 
  # Causes the “safe start violation” error to be cleared for 200 ms.
  # If there are no other errors, this allows the system to start up.
  def exit_safe_start(self):
    self.send_command(0x83)
 
  # Causes the Tic to stop the motor (using the configured soft error response behavior)
  # and set its “safe start violation” error bit.
  def enter_safe_start(self):
    self.send_command(0x8F)

  # Energize the stepper motor coils.
  def energize(self):
      self.send_command(0x85)

  # De-energize the stepper motor coils.
  def deenergize(self):
      self.send_command(0x86)

  # Resets and prevents the “command timeout” error from happening for some time. 
  def reset_command_timeout(self):
      self.send_command(0x8C)

  # Attempts to clear a motor driver error, which is an over-current or over-temperature
  # fault reported by the Tic’s motor driver. If the “Automatically clear driver errors”
  # setting is enabled (the default), the Tic will automatically clear a driver error and
  # it is not necessary to send this command. Otherwise, this command must be sent to
  # clear the driver error before the Tic can continue controlling the motor.
  def clear_driver_error(self):
      self.send_command(0x8a)

  # Reloads all settings from the Tic’s non-volatile memory and discards any temporary
  # changes to the settings previously made with serial commands (this applies to the
  # step mode, current limit, decay mode, max speed, starting speed, max acceleration,
  # and max deceleration settings).
  #
  # Abruptly halts the motor.
  # Resets the motor driver.
  # Sets the Tic’s operation state to “reset”.
  # Clears the last movement command and the current position.
  # Clears the encoder position.
  # Clears the serial and “command timeout” errors and the “errors occurred” bits.
  # Enters safe start if configured to do so.
  # 
  # The Tic’s serial and I²C interfaces will be unreliable for a brief period after the
  # Tic receives the Reset command, so a 100ms waiting period is included.
  def reset(self):
      self.send_command(0xB0)
      time.sleep(0.1)

  # Stops the motor abruptly without respecting the deceleration limit and sets the
  # “Current position” variable, which represents what position the Tic currently thinks
  # the motor is in. Besides stopping the motor and setting the current position, this
  # command also clears the “position uncertain” flag, sets the input state to “halt”,
  # and clears the “input after scaling” variable.
  # If not specified, sets position to 0.
  def halt_and_set_position(self, p=0):
      self.send_command(0xec, *write32(p))
      
  # Stops the motor abruptly without respecting the deceleration limit.
  # Sets the “position uncertain” flag.
  # Sets the input state to “halt”, and clears the “input after scaling” variable.
  def halt_and_hold(self):
      self.send_command(0x89)

  # Temporarily sets the Tic’s maximum allowed motor speed in units of steps per 10,000 seconds.
  def set_max_speed(self, v=500000000):
      self.send_command(0xE6, *write32(v))

  # Temporarily sets the Tic’s starting speed in units of steps per 10,000 seconds.
  def set_starting_speed(self, v=0):
      self.send_command(0xE5, *write32(v))

  # Temporarily sets the Tic’s maximum allowed motor acceleration
  # in units of steps per second per 100 seconds.
  def set_max_acceleration(self, a):
      self.send_command(0xEA, *write32(a))

  # Temporarily sets the Tic’s maximum allowed motor deceleration
  # in units of steps per second per 100 seconds.
  def set_max_deceleration(self, a):
      self.send_command(0xE9, *write32(a))

  # Temporarily sets the step mode (also known as microstepping mode) of the driver on the Tic,
  # which defines how many microsteps correspond to one full step.
  # 0: Full step
  # 1: 1/2 step
  # 2: 1/4 step
  # 3: 1/8 step
  # 4: 1/16 step (Tic T834 and Tic T825 only)
  # 5: 1/32 step (Tic T834 and Tic T825 only)
  def set_step_mode(self, m):
      self.send_command(0x94, m)

  # Temporarily sets the stepper motor coil current limit of the driver on the Tic
  # in units of 32 milliamps.
  # Range: 0 to 124
  def set_current_limit(self, i):
      self.send_command(0x91, i)

  # Temporarily sets the decay mode of the driver on the Tic.
  # Tic T500 (more information can be found in the MP6500 datasheet (1MB pdf)):
  # 0: Automatic
  # Tic T834 (more information can be found in the DRV8834 datasheet (2MB pdf)):
  # 0: Mixed 50%
  # 1: Slow
  # 2: Fast
  # 3: Mixed 25%
  # 4: Mixed 75%
  # Tic T825 (more information can be found in the DRV8825 datasheet (1MB pdf)):
  # 0: Mixed
  # 1: Slow
  # 2: Fast
  def set_decay_mode(self, m):
      self.send_command(0x92, m)
  
  def move_to_position(self, target):
    self.exit_safe_start()
    self.set_target_position(target)
    while not self.get_current_position() == target:
      # check limit switches 
      if self.limits:
        if target > self.get_current_position():
            direction = "top"
        else:
            direction = "bottom"
        limit = self.check_limit()
        if limit == "top" and direction == "top":
            self.halt_and_hold()
            self.set_target_position(target)
            self.top = True
            break
        elif limit == "bottom" and direction == "bottom":
            self.halt_and_hold()
            self.set_target_position(target)
            self.bottom = True
            break
      #need to reset command timeout, otherwise the stepper will only run for 1s
      time.sleep(0.1)
      self.reset_command_timeout()
    
    def move_to_limit(self, targetv):
        self.exit_safe_start()
        self.set_target_velocity(targetv)
        while True:
            limit = self.check_limit()
            if targetv < 0 and direction == "top":
                self.halt_and_hold()
                self.set_target_position(self.get_current_position())
                self.top = True
                break
            elif targetv > 0 and direction == "bottom":
                self.halt_and_hold()
                self.set_target_position(self.get_current_position())
                self.bottom = True
                break
            else:
                #need to reset command timeout, otherwise the stepper will only run for 1s
                time.sleep(0.1)
                tic.reset_command_timeout()
       

