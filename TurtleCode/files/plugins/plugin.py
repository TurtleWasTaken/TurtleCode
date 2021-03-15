## Create new class called: plugin
## Turtle Code will create an instance of this class

class plugin:
    _NAME_OVERRIDE_ = "Test Plugin"
    _MENU_COMMANDS_ = ["test", "hello there"]
    
    def __init__(self, tc):
        self.tc = tc

    '''def on_key_press(self, event):
        print(event)

    def on_mouse_move(self, event):
        print(event)

    def on_save(self, event):
        print(event)

    def on_load(self, event):
        print(event)

    def on_start(self, event):
        print(event)

    def on_menu_command(self, event):
        print(event)

    def on_quit(self, event):
        print(event)'''