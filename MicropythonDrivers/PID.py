import time 
 
class PID:
    def __init__(self, kp, ki, kd, limit):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limit = limit #should probably be 80
        self.reset()
        
        #limit essentialy caps the max possible speed that the
        #mouse can move
 
    def reset(self):
        "removes from memeory what the last state was"
        self.integral = 0
        self.last_error = None
        self.last_time = time.ticks_us()
 
    def update(self, error):
        """Give it the current error, get back the correction."""
        # How long since the last update seconds using real time
        now = time.ticks_us()
        dt = time.ticks_diff(now, self.last_time) / 1_000_000
        self.last_time = now
        if dt <= 0:
            dt = 0.001
 
        # P: push in proportion to how wrong we are right now
        p = self.kp * error
 
        # I: add up error over time; cancels a steady bias.
        
        self.integral += error * dt
        #idk bro
        i = self.ki * self.integral
        if self.ki and abs(i) > self.limit:
            i = self.limit if i > 0 else -self.limit
            self.integral = i / self.ki
 
        # D: how fast the error is changing; brakes before overshooting.
        if self.last_error is None:
            d = 0
        else:
            d = self.kd * (error - self.last_error) / dt
        self.last_error = error
 
        out = p + i + d
        return max(-self.limit, min(self.limit, out))
        
        
        