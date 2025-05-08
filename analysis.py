import math
import ujson
import json
import network
import time
from umqtt.simple import MQTTClient
from machine import ADC
from fifo import Fifo
from piotimer import Piotimer
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from oled_display import show_text
from heartrate import HeartRateMonitor
import ntptime

class MQTT:
    def __init__(self):
        self.SSID = "KMD652_Group_9"
        self.PASSWORD = "!GrandWorldTour2024"
        self.BROKER_IP = "192.168.50.23"  
        
    def connect_wlan(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.SSID, self.PASSWORD)

        while wlan.isconnected() == False:
            print("Connecting to KMD652_Group_9... ")
            sleep(2)
            
        print("Connection successful. Pico IP:", wlan.ifconfig()[0])
        
    def get_timestamp(self):
        try:
            self.connect_wlan()
            ntptime.settime()
            local_time = time.localtime(time.time() + 3*3600)
            timestamp = "{:02d}.{:02d}.{:04d} {:02d}:{:02d}".format(local_time[2], local_time[1], local_time[0], local_time[3], local_time[4])
            return timestamp
        except:
            timestamp = "jiihaa.pdf"
            return timestamp
        
        
    def connect_mqtt(self):
        mqtt_client=MQTTClient("", self.BROKER_IP, 21883)
        mqtt_client.connect(clean_session=True)
        return mqtt_client
    
    def send_message(self):
        mqtt_client= MQTT().connect_mqtt()
        topic = "hr-data"
        message = "Group 9 project message to mqtt!"
        mqtt_client.publish(topic, message)
        print(f"Sending to MQTT: {topic} -> {message}")

class HRV_monitor:
    def __init__(self, encoder):
        self.adc = ADC(26)
        self.data = Fifo(1300)
        self.previous_peak = 0
        self.bpm = 0
        self.thv = []
        self.threshold = 33000
        self.sample_number = 0
        self.current_peak = 0
        self.max_value = 0
        self.rising = False
        self.sample = 0
        self.previous_sample = 33000
        self.timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = self.get_sample)
        self.base_time = time.time()
        self.PPIs = []
        self.PPI = 0
        self.analysis = []
        self.encoder = encoder
        self.event = self.encoder.get_event()
        self.filter_window = []
        self.i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000) # siirä init
        self.oled_width = 128 # siirrä init
        self.oled_height = 64 # siirrä init
        self.oled = SSD1306_I2C(self.oled_width, self.oled_height, self.i2c) # siirrä init
        self.colour = 1 # siirrä init
        self.sectimer = False
        self.time_left = 30
        
        
    def get_sample(self, timer):
        self.sample = self.adc.read_u16()
        self.data.put(self.sample)
            
    def get_PPIs(self, encoder):
        running = True
        starting_time = time.time()
        while running == True:
            if self.data.has_data():
                raw = self.data.get()
                    
                self.sample_number += 1
                        
                self.thv.append(self.sample)
                if len(self.thv) >= 500:
                    self.threshold = (max(self.thv) + min(self.thv)) / 2
                    self.thv.clear()
                    
                # ordinary sample filtering
                filter = 0.05
                self.sample = raw # filter * raw + (1 - filter) * self.previous_sample

                if self.sample > self.threshold + 100:
                    if self.sample > self.max_value:
                        self.max_value = self.sample
                        self.current_peak = self.sample_number
                        self.rising = True
                        
                if self.sample < self.threshold and self.rising:
                    confirmed_peak = self.current_peak - self.previous_peak
                    self.previous_peak = self.current_peak
                    self.max_value = 0
                    self.rising = False
                    if 300 < confirmed_peak*4 < 1500 and confirmed_peak*4 != 0 and confirmed_peak != None:
                        self.PPI =confirmed_peak*4
                        print("PPI")
                        print(self.PPI)
                        self.PPIs.append(self.PPI)
                        
                self.event = self.encoder.get_event()
                if self.event == "SELECT":
                    if time.time() - starting_time >= 15:
                        self.time_left = True
                        running = False
                    else:
                        self.time_left = False
                        running = False

    def HRV_analysis(self):

        # mean PPI
        mean_ppi = sum(self.PPIs) / len(self.PPIs)
        
        # mean HR
        mean_hr = (60 / mean_ppi) * 1000
        
        # RMSSD
        sq_diff = []
        for i in range(1, len(self.PPIs)):
            diff = (self.PPIs[i] - self.PPIs[i-1])**2
            sq_diff.append(diff)
        if len(sq_diff) != 0: 
            mean_sq_diff = sum(sq_diff) / len(sq_diff)
            rmssd = math.sqrt(mean_sq_diff)

        # SDNN
        mean_intervals = sum(self.PPIs) / len(self.PPIs)
        sq_diff = []
        for i in range(1, len(self.PPIs)-1):
            from_mean = self.PPIs[i] - mean_intervals
            sq_diff.append(from_mean ** 2)
        average_difference = sum(sq_diff) / len(sq_diff)
        sdnn = math.sqrt(average_difference)
        
        # timestamp
        
        timestamp = print(MQTT().get_timestamp())
        MQTT().send_message()
        
        self.analysis = [timestamp, mean_ppi, mean_hr, rmssd, sdnn]
        
        # saving to a history.txt file
        with open("data.json", "w") as historydata:
            ujson.dump(self.analysis, historydata) 
        
        # MQTT function muuttujat analysis-listan valuet (analysis)

        return self.analysis
    
    def get_historydata(self):
        with open("data.json") as historydata:
            data = ujson.load(historydata)
        history_values = "{timestamp}, mean PPI: {data[0]}, mean HR: {data[1]}, RMSSD: {data[2]}, SDNN: {data[3]}"
        
        return data
    
    def draw_instructions(self):
        i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000) # siirä init
        oled_width = 128 # siirrä init
        oled_height = 64 # siirrä init
        oled = SSD1306_I2C(oled_width, oled_height, i2c) # siirrä init
        colour = 1 # siirrä init
        
        oled.fill(0)
        oled.text(f'min 30-second', 1, 2, 1)
        oled.text(f'sample needed', 1, 12, 1)
        oled.text(f'for HRV analysis', 1, 26, 1)
        oled.text(f'Press to begin', 1, 46, 1)
        oled.show()
        
    def draw_analysis(self):
        #Importit ja näytön määritys tulee jotenki ku laittaa draw(display)
        from machine import Pin, I2C
        from ssd1306 import SSD1306_I2C
        i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
        oled_width = 128
        oled_height = 64
        oled = SSD1306_I2C(oled_width, oled_height, i2c)
        colour = 1
        
        oled.fill(0)
        oled.text(f'Please hold', 15, 2, 1)
        oled.text(f'Measuring...', 21, 30, 1)
        oled.text(f'Calculating...', 29, 57, 1)
        oled.show()
    
    def draw_history(self):
        
        ddate = MQTT().get_timestamp()
        # placeholder muuttujat
        
        if len(self.analysis) > 0:
            self.oled.fill(0)
            self.oled.text(f'HRV analysis', 1, 2, 1)
            self.oled.text(f'{ddate}', 1, 12, 1)
            self.oled.text(f'Mean PPI: {self.analysis[0]}', 1, 26, 1)
            self.oled.text(f'Mean HR: {self.analysis[1]}', 1, 36, 1)
            self.oled.text(f'RMSDD: {self.analysis[2]}', 1, 46, 1)
            self.oled.text(f'SDNN: {self.analysis[3]}', 1, 56, 1)
            self.oled.show()
        else:
            self.oled.fill(0)
            self.oled.text(f'No data to show', 1, 36, 1)
            self.oled.show()

    def draw_error(self):
        if len(self.analysis) > 0:
            self.oled.fill(0)
            self.oled.text(f'HRV analysis', 1, 2, 1)
            self.oled.text(f'cancelled', 1, 12, 1)
            self.oled.text(f'Try again soon!', 1, 36, 1)
            self.oled.text(f'Press -> menu', 1, 46, 1)
            self.oled.show()
        else:
            self.oled.fill(0)
            self.oled.text(f'No data to show', 1, 34, 1)
            self.oled.show()
