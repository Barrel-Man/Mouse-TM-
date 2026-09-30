from machine import I2C, SoftI2C, Pin
import time
from micromouse import Micromouse
from PID import PID
from wallcentring import Walls, _mm
 
ticks_per_cell = 600    # travling ticks
ticks_per_90 = 520      # turning ticks
base_speed = 80         # 0..255
turn_speed = 60
slow_ticks = 100           # drop to half speed this many ticks before the cell ends
 
kp, ki, kd = 0.901, 0.0, 0.375
center_mm = 84          # side reading when centred
wall_mm = 120           # side wall exists if closer than this
#this is bulshit
front_wall_mm = 150     # front wall exists if closer than this (from cell centre)
front_stop_mm = 50      # emergency stop while driving
 
# mouse setup
 
left_i2c = I2C(0, sda = Pin(4), scl = Pin(5), freq = 100000)
front_i2c = I2C(1, sda = Pin(6), scl = Pin(7), freq = 400000)
right_i2c = SoftI2C(sda = Pin(0), scl = Pin(1), freq = 100000)
 
mm = Micromouse()
mm.invert_motor_2()
left_motor = mm.motor_2
right_motor = mm.motor_1
 
pid = PID(kp, ki, kd, base_speed//2)
walls = Walls(left_i2c, front_i2c, right_i2c, pid, center_mm, wall_mm)
 
left, front, right = 0, 1, 2
 
# Motor helper stuff
def stop():
    left_motor.spin_stop()
    right_motor.spin_stop()
    time.sleep_ms(200)
    
def _reset_encoders():
    left_motor.encoder_reset()
    right_motor.encoder_reset()
    
def _distance():
    #important this is avg distance travled
    l = left_motor.encoder_read()
    r = right_motor.encoder_read()
    return (abs(l) + abs(r)) // 2
 
def _dist(i):
    return _mm(walls.sensors[i]) #ts is calling distance in mm from wall
 
# moving
 
def spin(direction):
    _reset_encoders()
    while _distance() < ticks_per_90:
        left_motor.spin_power(direction * turn_speed)
        right_motor.spin_power(-direction * turn_speed)
    stop()
 
# these 3 names have to stay camelCase, AnActualStrat.py calls them
def turnRight():
    spin(1)
    
def turnLeft():
    spin(-1)
 
#idfk
def moveForward(distance = 1):
    for i in range(distance):
        _reset_encoders()
        pid.reset()
        while True:
            done = _distance()
            if done >= ticks_per_cell:
                break
            correction = walls.update()
            if walls.front is not None and walls.front < front_stop_mm:
                break
            if ticks_per_cell - done > slow_ticks:
                speed = base_speed
            else:
                speed = base_speed//2
            
            left_motor.spin_power(int(speed - correction))
            right_motor.spin_power(int(speed + correction))
        stop()
 
# Walls
def wallLeft():
    d = _dist(left)
    return d is not None and d < wall_mm
 
 
def wallRight():
    d = _dist(right)
    return d is not None and d < wall_mm
 
 
def wallFront():
    d = _dist(front)
    return d is not None and d < front_wall_mm
 
 
 # lazy
 
def setText(x, y, text):
    pass
 
 
def setWall(x, y, direction):
    pass
 
 
def setColor(x, y, color):
    pass
 
 
def clearAllColor():
    pass
 
def ackReset():
    stop()
    mm.led_green_set(1)
    time.sleep_ms(10000)  # gfoes after like 10 seconds
    mm.led_green_set(0)
    pass

#    def ackReset():
#        stop()
#        while not mm.get_button():
#            time.sleep_ms(20)
#        time.sleep_ms(1000)

                
        



