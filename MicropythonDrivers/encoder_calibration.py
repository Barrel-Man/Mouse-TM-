"""
calibrate.py - find TICKS_PER_CELL and TICKS_PER_90 for API.py.

Motors are off. Run this, then:
  1. Straight: push the mouse along a ruler exactly 160 mm (or 800 mm and
     divide by 5 - more accurate). The average of the two numbers = TICKS_PER_CELL.
  2. Turn: put it on paper, mark its heading, rotate it on the spot one full
     turn. Divide the average by 4 = TICKS_PER_90.
Press the button to zero the counts between tests.
"""
import time
from micromouse import Micromouse

mm = Micromouse()

while True:
    if mm.get_button():
        mm.motor_1.encoder_reset()
        mm.motor_2.encoder_reset()
        print("zeroed")
        time.sleep_ms(300)
    l, r = mm.get_encoders()
    print("left", l, "right", r, "avg", (abs(l) + abs(r)) // 2)
    time.sleep_ms(200)