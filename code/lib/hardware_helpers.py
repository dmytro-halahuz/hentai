import settings
from busio import SPI, UART, I2C
import displayio
from adafruit_st7735r import ST7735R
import pwmio
from DFPlayer import DFPlayer
import adafruit_ds3231
import analogio
from SH_converter import SH_converter
import time
import digitalio
from adafruit_debouncer import Debouncer
import os
import struct

class DisplayHelper:
    def __init__(self):
        self.backlight = pwmio.PWMOut(settings.display_backlight_pin, frequency=1000)
        self.set_brightness(0)

        self.curr_brightness = self.get_brightness_setting()

        displayio.release_displays()

        self.spi = SPI(settings.display_clock_pin, settings.display_mosi_pin)

        display_bus = \
            displayio.FourWire(
                self.spi,
                command=settings.display_command_pin,
                chip_select=settings.display_chip_select_pin,
                reset=settings.display_reset_pin)

        self.display = \
            ST7735R(
                display_bus,
                rotation=90,
                width=settings.display_width,
                height=settings.display_height,
                colstart=settings.display_colstart,
                rowstart=settings.display_rowstart, )

    def set_brightness(self, brightness_percent):
        self.backlight.duty_cycle = int(65535 / 100 * brightness_percent)

    def brighter(self):
        if self.curr_brightness < 100:
            self.curr_brightness += 5
            self.set_brightness(self.curr_brightness)

        return self.curr_brightness

    def dimmer(self):
        if self.curr_brightness > 5:
            self.curr_brightness -= 5
            self.set_brightness(self.curr_brightness)

        return self.curr_brightness

    def get_brightness_setting(self):
        curr_settings = settings.read_persistent_settings()
        return curr_settings["display_brightness_percent"]

    def save_setting(self):
        curr_settings = settings.read_persistent_settings()
        curr_settings["display_brightness_percent"] = self.curr_brightness
        settings.save_persistent_settings(curr_settings)


class DFPlayerHelper:
    def __init__(self):
        uart = UART(settings.dfplayer_tx_pin, settings.dfplayer_rx_pin, baudrate=settings.dfplayer_baudrate)
        self.curr_volume = self.get_volume_setting()
        volume = self.abs_volume(self.curr_volume)
        self.player = DFPlayer(uart, volume=volume, latency=0.1)
        self._ui_beep_index = self.player.num_files()

    def louder(self):
        if self.curr_volume < 100:
            self.curr_volume += 5
            self.player.set_volume(self.abs_volume(self.curr_volume))

        return self.curr_volume

    def quieter(self):
        if self.curr_volume > 0:
            self.curr_volume -= 5
            self.player.set_volume(self.abs_volume(self.curr_volume))

        return self.curr_volume

    def abs_volume(self, volume_percent):
        return settings.dfplayer_max_volume / 100 * volume_percent

    def play_track(self, track):
        self.player.play(track=track)

    def play_ui_beep(self):
        self.play_track(self._ui_beep_index)

    def get_volume_setting(self):
        return settings.read_persistent_settings()["dfplayer_volume"]

    def save_volume_setting(self):
        curr_settings = settings.read_persistent_settings()
        curr_settings["dfplayer_volume"] = self.curr_volume
        settings.save_persistent_settings(curr_settings)


class TimeHelper:
    def __init__(self):
        self.i2c = I2C(settings.clock_scl, settings.clock_sda)
        self.rtc = adafruit_ds3231.DS3231(self.i2c)

    def getTime(self):
        dt = self.rtc.datetime
        time = [dt.tm_hour, dt.tm_min]
        return time

    def setTime(self, new_time):
        dt = list(self.rtc.datetime)
        dt[3] = new_time[0]
        dt[4] = new_time[1]
        dt[5] = 0
        self.rtc.datetime = time.struct_time(dt)


class TempHelper:
    def __init__(self):
        curr_settings = settings.read_persistent_settings()
        points = curr_settings["temp_calibration_readings"]
        self.pin = analogio.AnalogIn(settings.temp_pin)
        self.converter = SH_converter.from_points(points)

    def getTemp(self):
        Sum = 0
        sample_size = 10
        for i in range(sample_size):
            Sum += self.pin.value
            time.sleep(0.05)
        r_ref = 10030
        v_ref = 65535
        v_in = Sum / sample_size
        r_T = r_ref * (v_ref / v_in - 1)

        return self.converter.temperature(r_T)


class ButtonHelper:
    def __init__(self):
        self.up_btn = self._setup_button(settings.up_btn_pin)
        self.down_btn = self._setup_button(settings.down_btn_pin)
        self.fwd_btn = self._setup_button(settings.fwd_btn_pin)
        self.back_btn = self._setup_button(settings.back_btn_pin)

    def _setup_button(self, pinN):
        pin = digitalio.DigitalInOut(pinN)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP
        return Debouncer(pin)

    def read_buttons(self):
        self.up_btn.update()
        self.down_btn.update()
        self.fwd_btn.update()
        self.back_btn.update()


class GifHelper:
    _gif_folder = "gif"

    def get_gif_paths(self):
        return [self._gif_folder + "/" + gif for gif in os.listdir(self._gif_folder)]

    def get_gif_names(self):
        return [gif.split('.')[0] for gif in os.listdir(self._gif_folder)]

    def get_intro_gif_index(self):
        intro_gif_file = settings.read_persistent_settings()["gif_file"]
        return self.get_gif_paths().index(intro_gif_file)

    def play_gif(self, odg):
        stngs = settings.read_persistent_settings()

        display = display_helper.display

        display_helper.set_brightness(stngs["display_brightness_percent"])
        start = time.monotonic()
        next_delay = odg.next_frame()  # Load the first frame
        end = time.monotonic()
        overhead = end - start
        #
        display.auto_refresh = False
        display_bus = display.bus
        #
        # Display repeatedly & directly.
        for f in range(odg.frame_count):
            # Sleep for the frame delay specified by the GIF,
            # minus the overhead measured to advance between frames.
            time.sleep(max(0, next_delay - overhead))
            next_delay = odg.next_frame()

            display_bus.send(42, struct.pack(">hh", 0, odg.bitmap.width - 1))
            display_bus.send(43, struct.pack(">hh", 0, odg.bitmap.height - 1))
            display_bus.send(44, odg.bitmap)

        display.auto_refresh = True


display_helper = DisplayHelper()
dfplayer_helper = DFPlayerHelper()
time_helper = TimeHelper()
temp_helper = TempHelper()
btn_helper = ButtonHelper()
gif_helper = GifHelper()
