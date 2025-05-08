from machine import Pin
import time
from fifo import Fifo

class RotaryEncoder:
    DEBOUNCE_MS = 200  # debounce

    def __init__(self, pin_a_num, pin_b_num, button_pin_num):
        self.pin_a = Pin(pin_a_num, Pin.IN, Pin.PULL_UP)
        self.pin_b = Pin(pin_b_num, Pin.IN, Pin.PULL_UP)
        self.button = Pin(button_pin_num, Pin.IN, Pin.PULL_UP)

        self.events = Fifo(16, typecode='B')  # FIFO 
        self.last_button_time = 0

        # Interupts
        self.pin_a.irq(trigger=Pin.IRQ_FALLING, handler=self._encoder_handler, hard=True)
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self._button_handler, hard=True)

    def _encoder_handler(self, pin):
        try:
            if self.pin_b.value() == 0:
                self.events.put(1)
            else:
                self.events.put(2)
        except (RuntimeError, AttributeError):
            pass

    def _button_handler(self, pin):
        try:
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_button_time) > self.DEBOUNCE_MS:
                if self.button.value() == 0:
                    try:
                        self.events.put(3)
                    except RuntimeError:
                        pass
                    self.last_button_time = now
        except (RuntimeError, AttributeError):
            pass


    def get_event(self):
        if self.events.has_data():
            try:
                event = self.events.get()
                if event == 1:
                    return "UP"
                elif event == 2:
                    return "DOWN"
                elif event == 3:
                    return "SELECT"
            except RuntimeError:
                pass
        return None
        
    #Functions to disable and enable interupts for navigation purposes
    def disable_interrupts(self):
        self.pin_a.irq(handler=None)
        self.button.irq(handler=None)
    
    def enable_interrupts(self):
        self.pin_a.irq(trigger=Pin.IRQ_FALLING, handler=self._encoder_handler, hard=True)
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self._button_handler, hard=True)


