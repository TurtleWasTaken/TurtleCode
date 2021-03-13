# Turtle Code

## Introduction

Turtle Code is a small, lightweight IDE I made in my spare time. It is currently in version 007.815, however I am still actively developing it.


## Features

- Syntax highlighting
- Auto-fill
- File management project system
- Script running (Needs work)


## Keybinds

- Ctrl + S  =>  Save
- Ctrl + Shift + S  =>  Save as
- Ctrl + O  =>  Open
- Ctrl + Shift + O  =>  Open folder as project
- Ctrl + R  =>  Run current file according to the "default_run_command" in the language folder of the current language.
- Shift + Tab  =>  Insert first word in auto-fill list (Right-side)

## Plugins

This section will go over the process of creating a plugin for Turtle Code. Plugins in Turtle Code are written in Python, and are located in the 'plugins' folder in 'files'.

- Step 1: Setting up the file
First navigate to Turtle Code's directory and enter: 'files/plugins'. Create a new python file, and name it the name of your plugin, then '.py'.

- Step 2: The 'plugin' class
Open your file up and make a new class called 'plugin'. This will be the backbone for your plugin. Here is a list of all of the global variables that Turtle Code will recognise:
    - _NAME_OVERRIDE_ :: Overrides the filename when naming the plugin. Useful for naming the plugin something with blacklisted file characters (like '\' or '/') or overriding previous plugins.
    - _MENU_COMMANDS_ :: A list of all the plugin's menubar commands that appear on the menubar (at 'Plugins\Plugins\{PLUGIN_NAME}')

Here is the list of all functions that Turtle Code will call:
    - __init__(self, tc) :: Called when the plugin is initialised (tc is a reference to the main class. Use it to interface with the program)
    - on_start(self, event) :: Same as __init__ but without tc
    - on_key_press(self, event) :: Called when any key is released
    - on_mouse_move(self, event) :: Called when the mouse is moved
    - on_save(self, event) :: Called when any file is saved
    - on_load(self, event) :: Called when any file is loaded
    - on_menu_command(self, event) :: Called when one of the plugin's menubar options is clicked
    - on_quit(self, event) :: Called just before the program closes



