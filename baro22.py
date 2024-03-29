#

from machine import Pin, I2C, Timer
from bmx280x import BMX280
from Carray import Circular_Array
import ssd1306py as oled
import utime

# OLED display
WIDTH  = 128                                            # oled display width
HEIGHT = 64                                             # oled display height

# barometer
BARO_ADDR= 118
ELEVATION = 0  # in metres above Sea Level
ALPHA = 0.8  # smoothing constant

global pressure
global pressure_old
global temperature
pressure_old = None
pressure = None
temperature = None

# baro history
history_interval_minutes = 12
history_length =  int(24 * 60 / history_interval_minutes) 
history = Circular_Array(history_length)
history_interval_sec =  history_interval_minutes * 60  
tendency_interval_index = int(3 * 60 / history_interval_minutes)   

# read and refresh display interval in sec
refresh_interval_sec=10 

#I2C
sda=machine.Pin(10)
scl=machine.Pin(11)
i2c=machine.I2C(1,sda=sda, scl=scl, freq=400000)

oled.init_i2c(11, 10, WIDTH, HEIGHT, 1)

# display mode 
global mode_i
button = machine.Pin(13,machine.Pin.IN,machine.Pin.PULL_DOWN)
button_timer = machine.Timer(-1)
modes=["current","graph","time"]
default_mode = 0
mode_i=default_mode
default_screen_interval_sec = 60


# initialise
baro = BMX280(i2c,BARO_ADDR)

# print(baro.chip_id)
# baro.print_calibration()

def adjust_for_elevation(pressure,elevation):
    return pressure +elevation/9.2

def read_pressure ():
    global pressure
    global pressure_old
    pressure_read = baro.pressure/100
    sl_pressure = round(adjust_for_elevation(pressure_read,ELEVATION),1)

    if pressure_old == None :
        pressure = sl_pressure
        pressure_old = pressure
    else :
        pressure_old = pressure 
        pressure = sl_pressure * ALPHA + pressure_old * (1-ALPHA)
     
def read_temperature() :
    global temperature
    temperature = baro.temperature

def get_change() :
    past_3hrs = history.val(tendency_interval_index)
    if past_3hrs != None :
        current = history.val(0)
        return current - past_3hrs
    else :
        return None
    
def tendency(change) :
# Met office forcast terminology
    rate = abs(change)
    if rate >0.1 :          
        if change  < 0:
            direction = "Falling"
        else :
            direction = "Rising"
                
        if rate  > 0.1 and rate  <= 1.5 :
            rate_qualifier =" slowly"
        elif rate  > 1.5 and rate <= 3.5 :
            rate_qualifier=""
        elif rate  >3.5 and rate <= 6.0 :
            rate_qualifier=" quickly"
        elif rate >6.0 :
            rate_qualifier=" v. quickly"
            
        return direction + rate_qualifier 
    else :
        return "Steady"

# displays
def splash() :
    oled.clear()
    oled.text("Ship",10,1,32)
    oled.text("Barometer",10,35,16)
    oled.show()


def display() :
    mode=modes[mode_i]
    
    if mode=="screensave":
        screensaver()
    elif mode == "current":
        data_screen()
    elif mode == "graph":
        graph_screen()
    elif mode == "time":
        time_screen()
 
def screen_saver() :
    oled.clear()
    oled.show()
    
def data_screen() :
    oled.clear()
    oled.text("{:.1f}".format(pressure),1,1,32)
    change = get_change()
    if change != None:
        oled.text( "Change "+ "{:.1f}".format(change)+ " mb",1,35,16)
        oled.text(tendency(change),1,50,16) 
    oled.show()

def change_screen() :
    oled.clear()
    change = get_change()
    if change != None:
        oled.text("Change "+ "{:.1f}".format(change),1,10,16)
        oled.text(tendency(change),1,20,16)
    else :
        oled.text("No data",1,20,16)
        
    oled.show() 

def time_screen() :
    oled.clear()
    running = utime.time() - start_time
    sec= int(running % 60)
    running = (running -sec) /60
    min = int(running % 60)
    running = (running - min) /60
    hr = int(running % 24)
    running = (running - hr) /24
    days = int(running)
    oled.text("running {} days ".format(days),1,20,8)
    oled.text("{:0>2d}:{:0>2d}:{:0>2d}".format(hr,min,sec),1,30,8)
    oled.text("Temp "+"{:.0f}".format(temperature),1,50,8)
    oled.show()
    
def bar(x,y,w,h):
    oled.fill_rect(x,63-y-h,w,h,1)

def line_bar(x,y,h) :
    oled.vline(x,63-y-h,h,1)
    
def graph_screen() :
    oled.clear()
    origin=980
    scale=1
    if history.length > 1 :
        for i in range(0,history.length) :
           j = history.length -1 - i
           h=  int((history.val(j) - origin ) * scale)
           line_bar(i,0,h)
   
    oled.show()
    
# mode button handling

def button_pressed(timer):
     global mode_i
     state = button.value()
     if state==1 :
        mode_i =(mode_i+1) % len(modes)
        display()
     button.irq(button_press,Pin.IRQ_RISING)

def button_press(pin) :
     button.irq(None)
     button_timer.init(mode=Timer.ONE_SHOT,period=200,callback=button_pressed)
   
# start button interrupt
button.irq(button_press,Pin.IRQ_RISING)
# startup screen
splash()
utime.sleep(2)

history_deadline = utime.time()
start_time=utime.time()
default_screen_deadline = utime.time()

while True:
    read_pressure()
    read_temperature()
    display()
    now_sec=utime.time()

# history update
    if now_sec > history_deadline :
        hpressure =round(pressure,1)
        history.push(hpressure)
        print ("history "+str(history.length)+" " +str(history.val(0)))
        history_deadline = now_sec + history_interval_sec

# default screen
    if now_sec > default_screen_deadline :
        mode_i = default_mode
        display()
        default_screen_deadline = now_sec + default_screen_interval_sec

    utime.sleep(refresh_interval_sec)

