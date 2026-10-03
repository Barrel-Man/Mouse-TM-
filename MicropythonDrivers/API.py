
from machine import I2C, SoftI2C, Pin
import time
from micromouse import Micromouse
from PID import PID
from wallcentring import Walls, _mm
 
ticks_per_cell = 20    # travling ticks
ticks_per_90 = 520      # turning ticks
base_speed = 80         # 0..255
turn_speed = 150        # power used for turning on the spot
turn_ms = 610           # how long a 90 degree turn spins for
slow_ticks = 100        
wall_samples = 3        
 
kp, ki, kd = 0.901, 0.0, 0.375
center_mm = 84          # side reading when centred
wall_mm = 120           # side wall exists if closer than this
#this is bulshit
front_wall_mm = 150     # front wall exists if closer than this (from cell centre)
front_stop_mm = 50      # emergency stop while driving
 
# mouse setup
 
right_i2c = I2C(0, sda = Pin(4), scl = Pin(5), freq = 100000)
front_i2c = I2C(1, sda = Pin(6), scl = Pin(7), freq = 100000)
left_i2c = SoftI2C(sda = Pin(0), scl = Pin(1), freq = 100000)
 
mm = Micromouse()
left_motor = mm.motor_2
right_motor = mm.motor_1
left_motor._invert = False
right_motor._invert = False
 
pid = PID(kp, ki, kd, base_speed//2)
walls = Walls(left_i2c, front_i2c, right_i2c, pid, center_mm, wall_mm)
 
left, front, right = 0, 1, 2
 
moving = False
stop_flag = False
 
def _correction():
    l = _mm(walls.sensors[left])
    r = _mm(walls.sensors[right])
    est = []
    if l is not None and l < wall_mm:
        est.append(l - center_mm)
    if r is not None and r < wall_mm:
        est.append(center_mm - r)
    if not est:
        return 0
    return - pid.update(sum(est) / len(est))
 
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
    left_motor.spin_power(direction * turn_speed)
    right_motor.spin_power(-direction * turn_speed)
    time.sleep_ms(turn_ms)
    stop()
 
#    def spin(direction):
#        _reset_encoders()
#        while _distance() < ticks_per_90:
#            left_motor.spin_power(direction * turn_speed)
#            right_motor.spin_power(-direction * turn_speed)
#        stop()
 
def turnRight():
    spin(-1)
    
def turnLeft():
    spin(1)
 
def check_far():
    d = _dist(front)
    if d is not None and 130 < d < 180:
        time.sleep_ms(100)
        left_motor.spin_power(base_speed)
        right_motor.spin_power(base_speed)
        time.sleep_ms(200)
        stop()
 
def check_close():
    d = _dist(front)
    if d is not None and d < 77:
        time.sleep_ms(100)
        left_motor._invert = True
        right_motor._invert = True
        left_motor.spin_power(base_speed)
        right_motor.spin_power(base_speed)
        time.sleep_ms(400)
        stop()
        left_motor._invert = False
        right_motor._invert = False
 
#idfk
def moveForward(distance = 1):
    global moving, stop_flag
    for i in range(distance):
        cell_mm = 160
        mm_per_sec = 51
        move_ms = int(cell_mm / mm_per_sec * 1000)
 
        pid.reset()
        stop_flag = False
        moving = True
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < move_ms:
            correction = _correction()
            if stop_flag:
                print("emergency stop")
                break
            left_motor.spin_power(int(base_speed - correction))
            right_motor.spin_power(int(base_speed + correction))
        moving = False
        stop()
        check_close()
        check_far()
 
# Walls
def _wall_seen(i, limit):
    votes = 0
    for _ in range(wall_samples):
        d = _dist(i)
        if d is not None and d < limit:
            votes += 1
    return votes * 2 > wall_samples
 
 
def wallLeft():
    return _wall_seen(left, wall_mm)
 
def wallRight():
    return _wall_seen(right, wall_mm)
 
def wallFront():
    return _wall_seen(front, front_wall_mm)
 
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
 
#    def ackReset():
#        stop()
#        while not mm.get_button():
#            time.sleep_ms(20)
#        time.sleep_ms(1000)
