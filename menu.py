from oled_display import show_menu

class Menu:
    def __init__(self, display, options):
        self.display = display
        self.options = options
        self.selected_index = 0

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % len(self.options)
        self.update_display()

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % len(self.options)
        self.update_display()

    def select(self):
        return self.options[self.selected_index]

    def update_display(self):
        show_menu(self.display, self.options, self.selected_index)
