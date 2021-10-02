#! /usr/bin/env python3
import time
import os

def take_action(direction):
    if direction not in ["up", "down"]:
        print("Unsupported direction %s, please choose up or down" % direction)
        return

    mot_ctrl = open ("/sys/class/gpio/gpio16/value", "wt")

    x_step = open ("/sys/class/gpio/gpio5/value", "wt")
    x_dir = open ("/sys/class/gpio/gpio6/value", "wt")

    if direction == "up":
        #print "up"
        x_dir.write ("0\n")
        os.system("aplay -D bluealsa:DEV=B8:D5:0B:B2:31:5C,PROFILE=a2dp bullshit.wav &")
    else:
        #print "down"
        x_dir.write ("1\n")
    x_dir.flush ()
    mot_ctrl.write ("0\n")
    mot_ctrl.flush ()

    steps = 0

    try:
        while steps < 1000:
            # first pause for setting the step high
            time.sleep (0.001)

            x_step.write ("1\n")
            x_step.flush ()

            # now pause for setting the step low
            time.sleep (0.001)

            x_step.write ("0\n")
            x_step.flush ()

            steps += 1
    except KeyboardInterrupt:
        pass

    mot_ctrl.write ("1\n")
    mot_ctrl.flush ()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: %s DIRECTION" % sys.argv[0])
        sys.exit(-1)

    direction = sys.argv[1].lower().strip()
    take_action(direction)

