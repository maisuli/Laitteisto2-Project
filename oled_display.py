from machine import I2C, Pin
import ssd1306

def init_display():
    i2c = I2C(1, scl=Pin(15), sda=Pin(14))
    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    display.fill(0)
    display.show()
    return display

def show_menu(display, options, selected_index):
    display.fill(0)
    for i, option in enumerate(options):
        prefix = ">" if i == selected_index else " "
        display.text(f"{prefix} {option}", 0, i * 12)
    display.show()

def show_text(display, text, line=0):
    display.fill(0)
    display.text(text, 0, line * 10)
    display.show()

