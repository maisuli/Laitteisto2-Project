from oled_display import init_display, show_menu
from menu import Menu
from rotary_encoder import RotaryEncoder
from heartrate import HeartRateMonitor
from analysis import HRV_monitor, MQTT
import time
from piotimer import Piotimer
from oled_display import init_display

class Monitor:
    def __init__(self):
        self.display = init_display()
        self.menu = Menu(self.display, ["Heart rate", "Analysis", "History", "Kubios"])
        self.encoder = RotaryEncoder(pin_a_num=10, pin_b_num=11, button_pin_num=12)
        self.state = self.start
        self.hr = HeartRateMonitor()
        self.hrv = HRV_monitor(self.encoder)
        
    def execute(self):
        while True:
            self.state()
    
    def encoder_check(self):
        event = self.encoder.get_event()
        while event != "SELECT":
            time.sleep(0.1)
            event = self.encoder.get_event()

    def start(self):
        self.menu.update_display()
        self.state = self.menu_state
        
    def menu_state(self):
        while self.state == self.menu_state:
            event = self.encoder.get_event()
            if event == "UP":
                self.menu.move_up()
            elif event == "DOWN":
                self.menu.move_down()
            elif event == "SELECT":
                selected = self.menu.select()
                if selected == "Heart rate":
                    self.state = self.heartrate
                elif selected == "Analysis":
                    self.state = self.analysis_instructions
                elif selected == "History":
                    self.state = self.history
                elif selected == "Kubios":
                    self.state = self.kubios

    def heartrate(self):
        self.hr.calculate_bpm()
        self.state = self.start
        
    def analysis_instructions(self):
        self.hrv.draw_instructions()
        event = self.encoder.get_event()
        self.encoder_check()
        self.state = self.analysis 
    
    def analysis(self):
        self.hrv.draw_analysis()
        self.hrv.get_PPIs(self.encoder)
        if self.hrv.time_left == True:
            self.hrv.HRV_analysis()
            self.hrv.draw_history()
            time.sleep(1)
            self.encoder_check()
        else:
            self.hrv.draw_error()
            self.encoder_check()
        self.state = self.start
    
    def history(self):
        self.hrv.draw_history()
        self.encoder_check()
        self.state = self.start # check coiko start ja menu olla sama vai alustaako jotain tarvittavaa

'''
    def kubios(self):
        from test_mqtt_kubios import connect_wlan, connect_mqtt, send_kubios_request
        connect_wlan()
        mqtt = connect_mqtt()
        send_kubios_request(mqtt)
        self.state = self.start
'''

Monitor().execute()