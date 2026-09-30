"""
main.py - wall-centering micromouse.

Files needed on the board: main.py, PID.py, wallcentring.py, micromouse.py,
motor.py, rotary.py, rotary_irq_rp2.py, VL53L0X.py
"""
"""
main.py - wall-centering micromouse.

Files needed on the board: main.py, PID.py, wallcentring.py, micromouse.py,
motor.py, rotary.py, rotary_irq_rp2.py, VL53L0X.py

from machine import I2C, SoftI2C, Pin
import time
from micromouse import Micromouse
from PID import PID
from wallcentring import Walls

# ---------------- I2C BUSES (one per ToF sensor) ----------------
LEFT_I2C  = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
FRONT_I2C = I2C(1, sda=Pin(6), scl=Pin(7), freq=400000)
RIGHT_I2C = SoftI2C(sda=Pin(0), scl=Pin(1), freq=100000)



# ---------------- SETTINGS ----------------
CALIBRATE = False # True = motors off, just print sensor readings
BASE_SPEED = 80          # 0..255
KP, KI, KD = 0.901, 0.0, 0.375
CENTER_MM = 84          # side reading when centred (measure with CALIBRATE)
WALL_MM = 120
FRONT_STOP_MM = 70

# ---------------- MOUSE ----------------
mm = Micromouse()
# Micromouse() already inverts motor_2. The sample code for this board
# flips it back to match the wiring - remove this line if your mouse
# then drives backwards or spins in circles instead of straight.
mm.invert_motor_2()

LEFT_MOTOR = mm.motor_2
RIGHT_MOTOR = mm.motor_1

# ---------------- SETUP ----------------
pid = PID(KP, KI, KD, limit=BASE_SPEED // 2)
walls = Walls(LEFT_I2C, FRONT_I2C, RIGHT_I2C, pid, CENTER_MM, WALL_MM)

loop = 0
try:
    while True:
        if CALIBRATE:
            print("L F R:", walls.read())
            time.sleep_ms(100)
            continue

        correction = walls.update()

        if walls.front is not None and walls.front < FRONT_STOP_MM:
            print("Front wall, stopping")
            break

        # correction > 0 -> left wheel faster -> turn right (and vice versa)
        # int() needed: Motor.spin_power crashes on floats
        left_power = int(BASE_SPEED - correction)
        right_power = int(BASE_SPEED + correction)
        LEFT_MOTOR.spin_power(left_power)
        RIGHT_MOTOR.spin_power(right_power)

        loop += 1
        if loop % 10 == 0:      # print every 10th loop; printing every loop slows it down
            print(walls.walls, walls.left, walls.right,
                  "err %.1f cor %.1f" % (walls.error, correction),
                  left_power, right_power)
finally:
    LEFT_MOTOR.spin_stop()
    RIGHT_MOTOR.spin_stop()
"""
import time
import API             
import AnActualStrat

try:
    AnActualStrat.main()
finally:
    API.stop()