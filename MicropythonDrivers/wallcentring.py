from machine import Pin
import time
import VL53L0X
 
 
def _start(i2c):
    try:
        s = VL53L0X.VL53L0X(i2c)    # default address 0x29
        s.start()                   # continuous ranging
        return s
    except Exception as e:
        print("tof init failed", i2c, e)
        return None
 
 
def _mm(sensor):
    try:
        d = sensor.read()
    except Exception:
        return None
    return None if d >= 8000 else d
 
 
class Walls:
    def __init__(self, left_i2c, front_i2c, right_i2c, pid, center_mm, wall_mm):
        self.sensors = (_start(left_i2c), _start(front_i2c), _start(right_i2c))
        self.pid = pid
        self.center = center_mm      # side reading when centred
        self.wall_mm = wall_mm
 
        self.left = self.front = self.right = None
        self.walls = None            # (left_wall, right_wall) last loop
        self.error = 0
 
    def read(self):
        """(left, front, right) in mm. None = nothing in range."""
        return tuple(_mm(s) for s in self.sensors)
 
    def update(self):
        """Read sensors -> error -> PID. Returns the steering correction."""
        self.left, self.front, self.right = self.read()
 
        left_wall = self.left is not None and self.left < self.wall_mm
        right_wall = self.right is not None and self.right < self.wall_mm
 
        # Walls appeared/disappeared -> error may jump, so restart the PID
        if (left_wall, right_wall) != self.walls:
            self.pid.reset()
            self.walls = (left_wall, right_wall)
 
        estimates = []
        if left_wall:
            estimates.append(self.left - self.center)
        if right_wall:
            estimates.append(self.center - self.right)
 
        if not estimates:
            self.error = 0
            return 0 
 
        self.error = sum(estimates) / len(estimates)
        return self.pid.update(self.error)
