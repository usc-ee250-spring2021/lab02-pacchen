""" EE 250L Lab 02: GrovePi Sensors

List team members here.
Insert Github repository link here.

"""

"""python3 interpreters in Ubuntu (and other linux distros) will look in a
default set of directories for modules when a program tries to `import` one.
Examples of some default directories are (but not limited to):
  /usr/lib/python3.5
  /usr/local/lib/python3.5/dist-packages

The `sys` module, however, is a builtin that is written in and compiled in C for
performance. Because of this, you will not find this in the default directories.
"""
import sys
import time
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('../../Software/Python/')
# This append is to support importing the LCD library.
sys.path.append('../../Software/Python/grove_rgb_lcd')

import grovepi

#setting up potentiometer
potentiometer = 0
grovepi.pinMode(potentiometer,"INPUT")
time.sleep(1)

#LCD
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)
"""This if-statement checks if you are running this python file directly. That
is, if you run `python3 grovepi_sensors.py` in terminal, this if-statement will
be true"""
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)


#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    while len(text) < 32: #clears the rest of the screen
        text += ' '
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

if __name__ == '__main__':
    PORT = 4    # D4
    Threshold = 0;
    sensor_value = grovepi.analogRead(potentiometer)
    sensor_v = 0;
    setRGB(255,255,255)
    status = "";
    while True:

        #So we do not poll the sensors too quickly which may introduce noise,
        #sleep for a reasonable time of 200ms between each iteration.
        time.sleep(0.1)
        #gather data
        sensor_value = grovepi.analogRead(potentiometer)
        ultra_dis = grovepi.ultrasonicRead(PORT)

            
        #as potentiometer won't stay in one same value
        if (abs(sensor_value - sensor_v) >2):
            Threshold = round(float(sensor_value) /1023*517)
            setText_norefresh("{:>3}CM {}".format(str(Threshold),status))
            sensor_v = sensor_value
        
        #ultra_dis max 495 for me
        if (Threshold > ultra_dis and status == ""):
            setRGB(255,0,0)
            status = "OBJ PRES"
            setText_norefresh("{:>3}CM {}".format(str(Threshold),status))
        elif (Threshold < ultra_dis and status == "OBJ PRES"):
            setRGB(255,255,255)
            status = ""
            setText_norefresh("{:>3}CM {}".format(str(Threshold),status))



        #displaying second row
        setText_norefresh("\n{:>3}CM".format(str(ultra_dis)))
        
        print("sensor_value = %d ultra_dis = %d Threshold = %d status " %(sensor_value, ultra_dis, Threshold)+status)
