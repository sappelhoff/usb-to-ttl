:orphan:

.. _code-examples:

Code examples
=============

For using these code snippets, you will have to have your hardware (e.g., based on the Arduino Leonardo) connected to a USB port of your computer.
Next, you will have to find out the port that your computer assigned to the USB device.
This requires a different procedure, depending on the operating system.

- Windows: Open the "Device Manager" and look at the Ports list (COM & LPT). The ports usually have names like ``"COM*"``.
- Linux and OSX: Check the devices in ``/dev/`` through ``ls /dev/*``. The port names differ between Linux and OSX:

  - Linux: usually ``/dev/ttyUSB*`` or ``/dev/ttyACM*``

  - OSX: usually ``/dev/tty.usbmodem*`` or ``/dev/tty.usbserial*``

The Python section below shows a way how to find the ports using the ``pyserial`` library.

Python
------

You will need to install the `pyserial`_ package via ``pip install pyserial``.

Find the port
^^^^^^^^^^^^^

We can use ``pyserial`` to find the port of our USB device

.. code-block:: python

   import serial  # imports pyserial
   import serial.tools.list_ports as list_ports

   # List all comports
   all_ports = list_ports.comports()
   print(all_ports)

   # Each entry in the `all_ports` list is a serial device. Check it's
   # description and device attributes to learn more
   first_serial_device = all_ports[0]
   print(first_serial_device.device)  # the `port_name`
   print(first_serial_device.description)  # perhaps helpful to know if this is your device

   # continue until you found your device, then note down the `port_name`

Send information
^^^^^^^^^^^^^^^^

Now open up a serial connection and send some information.

.. code-block:: python

   import serial

   port_name = "COM4"  # the name / address we found for our device

   ser = serial.Serial(
       port=port_name,
       baudrate=115200,
       bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
       )

   # the information we want to send: 8 bits = 1 byte
   byte_to_send = bytes([1])  # send a "1"
   ser.write(byte_to_send)

Consider sampling rate of recording device
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For event marking, we usually want to start with a state of ``0``, then set the data to some byte (e.g., ``1``), and finally reset the state to ``0`` again.
Notably, the time that the data is set to a byte different from ``0`` needs to be long enough for our recording device to notice.
Practically, this depends on the sampling rate: At a sampling rate of 1000Hz, the data needs to be "switched on" for *at least* 1ms (at a sampling rate of 250Hz, for 4ms, etc.).

.. code-block:: python

   import serial
   from time import perf_counter

   # Define a function to help us accurately wait a certain amount of time
   def mysleep(waitsecs):
   """Block execution of further code for `waitsecs` seconds."""
       twaited = 0
       start = perf_counter()
       while twaited < waitsecs:
           twaited = perf_counter() - start

   ser = serial.Serial(
       port="COM4",
       baudrate=115200,
       bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
       )

   # Set data status to `0`
   ser.write(bytes([0]))

   # Let's send some information: Bytes from 1 to 10
   # We assume that our recording device has a sampling rate of 1000Hz
   for data in range(1, 10):
       byte_to_send = bytes([data])

       ser.write(byte_to_send)  # send data
       mysleep(waitsecs=0.001)  # wait for 1ms for recording device to catch this
       ser.write(bytes([0]))  # reset data status to `0`


.. _pyserial: https://github.com/pyserial/pyserial
