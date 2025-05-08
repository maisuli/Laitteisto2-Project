from machine import ADC
from piotimer import Piotimer
from fifo import Fifo
import time
from oled_display import init_display

class HeartRateMonitor:
    def __init__(self):
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
        self.bpm_updated = False
        self.samples = []
        self.bpms = []
        

    def get_sample(self, timer):
        self.sample = self.adc.read_u16()
        self.data.put(self.sample)

    def calculate_bpm(self):
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
        display.text('Press to exit', 10, 2, 1)
        display.text(f"Measuring...", 32, 35, 1)
        display.show()
        
        while True:
            if self.data.has_data():
                raw = self.data.get()
                self.sample_number += 1

                # ordinary sample filtering
                alpha = 0.1
                self.sample = alpha * raw + (1 - alpha) * self.previous_sample
                    
                self.thv.append(self.sample)
                if len(self.thv) >= 250:
                    self.threshold = (max(self.thv) + min(self.thv)) / 2
                    self.thv.clear()

                '''
                # rolling average filtering
                self.samples.append(self.sample)
                if len(self.samples) > 20:
                    data = self.samples[-10:]
                    sample = sum(data)/len(data)
                    data2 = self.samples[-20:-10]
                    self.sample = sum(data2)/len(data2)
                    self.samples = self.samples[-20:]
                '''


                if self.sample > self.threshold + 100:
                    if self.sample > self.max_value:
                        self.max_value = self.sample
                        self.current_peak = self.sample_number
                        self.rising = True
                    
                if self.sample < self.threshold and self.rising:
                    confirmed_peak = self.current_peak - self.previous_peak
                    if confirmed_peak != 0:
                        self.previous_peak = self.current_peak
                        self.max_value = 0
                        self.rising = False
                                
                        bpm_init = 60000 / (confirmed_peak*4) # 4 ms between samples
                        if 40 < bpm_init < 200: # general ordinary heart rate min & max
                            self.bpm = bpm_init
                            self.bpms.append(self.bpm)
                            
                print(self.bpms)
             
                
                    
                # timer to print value every 5 seconds + calculating 5 sec average bpm
                current_time = time.time()
                if current_time - self.base_time >= 5:
                    if len(self.bpms) > 0:
                        self.bpm = sum(self.bpms)/len(self.bpms)
                        self.bpms.clear()
                        self.bpm_updated = True
                        self.base_time = current_time
                        print(self.bpm)
                        
                if self.bpm_updated:
                    display.fill_rect(0, 35, 128, 8, 0)  # Tyhjennä pelkkä BPM:n alue
                    display.text(f"{int(self.bpm)} BPM", 32, 35, 1)
                    self.bpm_updated = False
                                      
                self.previous_sample = raw
                
                display.show()

#HeartRateMonitor().calculate_bpm()
