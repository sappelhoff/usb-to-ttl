#!/usr/bin/env python
"""Measure TTL trigger sending latency of several devices.

Required packages:

- numpy (https://pypi.org/project/numpy/)
- psychtoolbox (https://pypi.org/project/psychtoolbox/)
- pylsl (https://pypi.org/project/pylsl/)
- pyparallel (https://pypi.org/project/pyparallel/)

"""

import os
import sys
import time

import numpy as np
import pylsl
import psychtoolbox as ptb

port = sys.argv[1]

# Define the "send_trigger" function depending on which device we are testing
if port == 'parport':
    if os.name == 'nt':
        from psychopy.parallel import ParallelPort as PP
    else:
        from parallel import Parallel as PP
    parport = PP()

    def send_trigger():
        parport.setData(1)
        time.sleep(.005)
        parport.setData(0)

elif port == 'labjack':
    import u3
    lj = u3.U3()

    def send_trigger():
        # Using the U3, we can either use the writeRegister method, ...
        # or the setFIOState method.
        lj.writeRegister(6700, 0xFF01)
        # lj.setFIOState(0, 1)
        time.sleep(.01)
        lj.writeRegister(6700, 0xFF00)
        # lj.setFIOState(0, 0)

else:
    # serial port
    ser, _ = ptb.IOPort('OpenSerialPort', port,
                        'BaudRate=115200 FlowControl=None ReceiveTimeout=0.05')

    def send_trigger():
        ptb.IOPort('Write', ser, '\x01')
        # "Sleep" is handled by firmware on device
        # Flush incoming data
        _, _, err = ptb.IOPort('Read', ser, 1, 3)

# Create an LSL outlet
outlet = pylsl.StreamOutlet(
    pylsl.StreamInfo(name='latencytest',
                     type='marker',
                     channel_count=1,
                     nominal_srate=pylsl.IRREGULAR_RATE,
                     channel_format=pylsl.cf_string))

# Get the psychHID index for the emulated keyboard
try:
    kbdidx = next(
        (dev['index'] for dev in ptb.PsychHID('devices', 4)
         if dev['product'].startswith('Teensyduino'))
    )
except StopIteration:
    kbdidx = 0

# Initialize the Psychtoolbox keyboard queue
keycode = 12 if os.name == 'nt' else 36
keys = np.zeros(256)
keys[keycode] = 1
ptb.PsychHID('KbQueueCreate', kbdidx, keys)
ptb.PsychHID('KbQueueStart', kbdidx)

# Call both functions once to make sure the C libraries are loaded
pylsl.local_clock()
ptb.GetSecs()

# Make sure LSL and PTB use the same underlying clock
timediff = abs(
    pylsl.local_clock()-ptb.GetSecs()+ptb.GetSecs()-pylsl.local_clock()
)
assert(timediff < 1e-3)

while True:
    # Wait for the Teensy to simulate a keypress
    ptb.PsychHID('KbQueueFlush', kbdidx, 3)
    event, n = ptb.PsychHID('KbQueueGetEvent', kbdidx, 1)
    t0 = pylsl.local_clock()
    # Don't send a trigger when waiting for the keypress timed out or the event
    # signified the key release (as opposed to initially pressing it down)
    if len(event) == 0 or event['Pressed'] == 0:
        continue

    send_trigger()  # Send a trigger via the configured interface

    # Send an LSL event with the previously measured time to the LabStreamer
    outlet.do_push_sample(
        outlet.obj,
        outlet.sample_type(b'1'),
        pylsl.pylsl.c_double(t0),
        pylsl.pylsl.c_int(True))
