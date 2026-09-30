"""
tof.py - simple driver for one VL53L0X time-of-flight sensor.
Wraps VL53L0X.py so main.py just calls tof.distance_mm().
"""
from machine import Pin, I2C
import VL53L0X


class ToF:
    def __init__(self, sda, scl, i2c_id):
        # GP2, GP6, GP10, GP14, GP18, GP26GP3, GP7, GP11, GP15, GP19, GP26, [i2c 1]
        # GP0, GP4, GP8, GP12, GP16, GP20, GP28GP1, GP5, GP9, GP13, GP17, GP21, GP27, [i2c 0]
        self.i2c = I2C(i2c_id, sda=Pin(sda), scl=Pin(scl), freq=400000)
        print("I2C devices:", [hex(a) for a in self.i2c.scan()])  # want 0x29  
        self.sensor = VL53L0X.VL53L0X(self.i2c)
        self.sensor.start()  # continuous ranging
    
    

    def distance_mm(self):
        return self.sensor.read()
