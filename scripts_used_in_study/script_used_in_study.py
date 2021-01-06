#!/usr/bin/env python

import os
import pylsl
import serial
import sys
import time

if os.name == 'nt':
    from psychopy.parallel import ParallelPort as PP
else:
    from parallel import Parallel as PP

com = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'

# serial port
ser = serial.Serial(com, 115200, xonxoff=False, rtscts=False, dsrdtr=False, write_timeout=0)
# parallel port
pp = PP()

# LSL outlet
outlet = pylsl.StreamOutlet(
    pylsl.StreamInfo(name='latencytest',
                     type='marker',
                     channel_count=1,
                     nominal_srate=pylsl.IRREGULAR_RATE,
                     channel_format=pylsl.cf_string))

while True:
    t = pylsl.local_clock()  # get trial start time
    pp.setData(1)  # set parallel port output pin to high
    ser.write(b'5')  # send the trigger to the serial device
    time.sleep(.001)  # sleep 1ms
    pp.setData(0)  # set the parallel port output pin to low
    # send an LSL event with the previously measured time to the LabStreamer
    outlet.do_push_sample(
        outlet.obj,
        outlet.sample_type(b'1'),
        pylsl.pylsl.c_double(t),
        pylsl.pylsl.c_int(True))

    # wait for the Teensy to simulate a keypress
    sys.stdin.read(1)
    ser.reset_input_buffer()
