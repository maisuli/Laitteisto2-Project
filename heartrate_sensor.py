import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from heartrate import HeartRateMonitor
from oled_display import init_display
from alt_main import Monitor

def start_measurement(display, encoder):
    av = ADC(26)
    hr_monitor = HeartRateMonitor()
    
    display = init_display()

    # Range
    old_min = 30000
    old_max = 39000
    new_min = 12
    new_max = 48
    old_range = old_max - old_min
    new_range = new_max - new_min

    list = [128, 128]

    x = 0

    display.fill(0)
    display.text(f"...", 48, 57, 1)

    while True:
        
        '''
        event = encoder.get_event()
        
        if event == "SELECT":
            hr_monitor.stop()
            #encoder.disable_interrupts()  
            time.sleep_ms(100)            
            break
        '''
        
        value1 = self.sample
        
        if hr_monitor.bpm_updated:
            display.fill_rect(0, 56, 128, 8, 0)  # Tyhjennä pelkkä BPM:n alue
            display.text(f"{int(monitor.bpm)} BPM", 32, 57, 1)
            hr_monitor.bpm_updated = False
        
        if hr_monitor.bpm_updated:
            display.fill_rect(0, 56, 128, 8, 0)  # Tyhjennä pelkkä BPM:n alue
            display.text(f"{int(hr_monitor.bpm)} BPM", 32, 57, 1)
            hr_monitor.bpm_updated = False
     
        display.text('Press to exit', 10, 2, 1)
                
        if value1 < old_max and value1 > old_min:
            # scale value
            value2 =  (((value1 - old_min) * new_range) / old_range)
            # inverse value
            value3 = 0 + (new_max - value2)
            value3 = round(value3)
            
            list[0] = list[1]
            list[1] = value3
            

            
            if x < 128:
                x2 = x - 1
                y = list[0]
                y2 = list[1]
                display.line(x, y, x2, y2, 1)
                display.show()
                x = x + 2
            
            if x == 128:
                x2 = x - 1
                y = list[0]
                y2 = list[1]
                display.line(x, y, x2, y2, 1)
                display.show()
                display.fill_rect(0, 12, 128, 44, 0)
                display.show()
                x = 0              
        

