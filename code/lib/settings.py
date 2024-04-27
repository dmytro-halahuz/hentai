import json

import board
# buttons
up_btn_pin = board.GP19
down_btn_pin = board.GP18
fwd_btn_pin = board.GP16
back_btn_pin = board.GP17

# display
display_backlight_pin = board.GP13
display_clock_pin = board.GP10
display_mosi_pin = board.GP11
display_command_pin = board.GP8
display_chip_select_pin = board.GP9
display_reset_pin = board.GP12

display_width = 128
display_height = 128
display_colstart = 2
display_rowstart = 3

# DFPlayer
dfplayer_tx_pin = board.GP4
dfplayer_rx_pin = board.GP5
dfplayer_baudrate = 9600

dfplayer_max_volume = 80

# Clock
clock_scl = board.GP21
clock_sda = board.GP20

# Temperature
temp_pin = board.GP26

settings_file_name = "settings.json"

default_settings =\
{
    "dfplayer_volume": 80,
    "display_brightness_percent": 100,
    "gif_file": "",
    "intro_sound_index": 0,
    "temp_calibration_readings":
        (
            (-16, 33000),
            (8, 10000),
            (22.7, 5333)
        ),
    "ui_text_color": 0xffffff
}

def save_persistent_settings(settings):
    settings_file = open(settings_file_name, "w")
    json.dump(settings, settings_file)
    settings_file.close()


def read_persistent_settings():
    try:
        settings_file = open(settings_file_name, "r")
    except:
        save_persistent_settings(default_settings)
        return default_settings

    settings = json.load(settings_file)
    settings_file.close()
    return settings
