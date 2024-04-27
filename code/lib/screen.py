from adafruit_button import Button
from terminalio import FONT
import displayio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from hardware_helpers import time_helper, temp_helper, display_helper, dfplayer_helper, gif_helper
import time
import settings
import microcontroller
import re


class Screen:
    _background_color = 0x000000
    _text_color = settings.read_persistent_settings()["ui_text_color"]
    _screen_width = 128
    _screen_height = 128

    def __init__(self, prev_screen=None):
        self._group = displayio.Group()
        if prev_screen is None:
            self.prev_screen = self
        else:
            self.prev_screen = prev_screen

    def show(self):
        display_helper.display.root_group = self._group

    def up(self):
        dfplayer_helper.play_ui_beep()
        return self

    def down(self):
        return self

    def back(self):
        return self.prev_screen

    def forward(self):
        return self


class ClockScreen(Screen):
    def __init__(self):
        super().__init__()

        font = bitmap_font.load_font("FSSevegment-40.bdf", displayio.Bitmap)
        font_small = bitmap_font.load_font("FSSevegment-30.bdf", displayio.Bitmap)

        self._display_dots = True

        bitmap = displayio.Bitmap(128, 128, 1)
        bitmap.fill(0)
        pal = displayio.Palette(1)
        pal[0] = self._background_color
        background = displayio.TileGrid(bitmap, pixel_shader=pal)

        self._clock_area = (
            label.Label(
                font,
                text=self._getTime(),
                color=self._text_color,
                anchor_point=(0.5, 1.0)
            )
        )
        self._clock_area.anchored_position = (64, 60)

        self._temp_area = (
            label.Label(
                font_small,
                text=self._getTemp(),
                color=self._text_color,
                anchor_point=(0.5, 0.0)
            )
        )
        self._temp_area.anchored_position = (64, 68)

        self._group.append(background)
        self._group.append(self._clock_area)
        self._group.append(self._temp_area)

    def show(self):
        self._clock_area.text = self._getTime()
        self._temp_area.text = self._getTemp()
        display_helper.display.root_group = self._group
        time.sleep(0.4)

    def _getTemp(self):
        return str(round(temp_helper.getTemp(), 1)) + "°C"

    def _getTime(self):
        curr_time = time_helper.getTime()
        if self._display_dots:
            time = "{:02d}".format(curr_time[0]) + ":" + "{:02d}".format(curr_time[1])
        else:
            time = "{:02d}".format(curr_time[0]) + " " + "{:02d}".format(curr_time[1])

        self._display_dots = not self._display_dots

        return time

    def back(self):
        microcontroller.reset()

    def forward(self):
        return MainMenu(self)


class ClockSettingScreen(Screen):
    def __init__(self, prev_screen):
        super().__init__(prev_screen)
        font = bitmap_font.load_font("FSSevegment-40.bdf", displayio.Bitmap)

        self._hh_selected = True
        self.curr_time = time_helper.getTime()

        bitmap = displayio.Bitmap(128, 128, 1)
        bitmap.fill(0)
        pal = displayio.Palette(1)
        pal[0] = self._background_color
        background = displayio.TileGrid(bitmap, pixel_shader=pal)

        dot_area = (
            label.Label(
                font,
                text=":",
                color=self._text_color,
                anchor_point=(0.5, 0.5)
            )
        )

        dot_area.anchored_position = (64, 64)

        padding = 2

        self._hh_area = (
            label.Label(
                font,
                text=self._format(self.curr_time[0]),
                color=self._text_color,
                anchor_point=(1.0, 0.5),
                padding_top=padding,
                padding_left=padding,
                padding_bottom=padding
            )
        )
        self._hh_area.anchored_position = (64 - dot_area.width / 2, 64)

        self.select_area(self._hh_area)

        self._mm_area = (
            label.Label(
                font,
                text=self._format(self.curr_time[1]),
                color=self._text_color,
                anchor_point=(0.0, 0.5),
                padding_top=padding,
                padding_left=padding,
                padding_bottom=padding

            )
        )
        self._mm_area.anchored_position = (64 + dot_area.width / 2, 64)

        self._group.append(background)
        self._group.append(dot_area)
        self._group.append(self._hh_area)
        self._group.append(self._mm_area)

    def _format(self, time):
        return "{:02d}".format(time)

    def select_area(self, area):
        area.background_color = self._text_color
        area.color = self._background_color

    def unselect_area(self, area):
        area.background_color = self._background_color
        area.color = self._text_color

    def down(self):
        dfplayer_helper.play_ui_beep()
        if self._hh_selected:
            if self.curr_time[0] > 0:
                self.curr_time[0] -= 1
                self._hh_area.text = self._format(self.curr_time[0])
                time_helper.setTime(self.curr_time)
            else:
                self.curr_time[0] = 23
                self._hh_area.text = self._format(self.curr_time[0])
                time_helper.setTime(self.curr_time)
        else:
            if self.curr_time[1] >= 1:
                self.curr_time[1] -= 1
                self._mm_area.text = self._format(self.curr_time[1])
                time_helper.setTime(self.curr_time)
            else:
                self.curr_time[1] = 59
                self._mm_area.text = self._format(self.curr_time[1])
                time_helper.setTime(self.curr_time)

        return self

    def up(self):
        dfplayer_helper.play_ui_beep()
        if self._hh_selected:
            if self.curr_time[0] < 23:
                self.curr_time[0] += 1
                self._hh_area.text = self._format(self.curr_time[0])
                time_helper.setTime(self.curr_time)
            else:
                self.curr_time[0] = 0
                self._hh_area.text = self._format(self.curr_time[0])
                time_helper.setTime(self.curr_time)
        else:
            if self.curr_time[1] < 59:
                self.curr_time[1] += 1
                self._mm_area.text = self._format(self.curr_time[1])
                time_helper.setTime(self.curr_time)
            else:
                self.curr_time[1] = 0
                self._mm_area.text = self._format(self.curr_time[1])
                time_helper.setTime(self.curr_time)
        return self

    def back(self):
        if self._hh_selected:
            return self.prev_screen
        else:
            self.unselect_area(self._mm_area)
            self.select_area(self._hh_area)
            self._hh_selected = True
            return self

    def forward(self):
        if self._hh_selected:
            self.unselect_area(self._hh_area)
            self.select_area(self._mm_area)
            self._hh_selected = False
        return self


class VolumeMenu(Screen):
    def __init__(self, prev_screen):
        super().__init__(prev_screen)
        self.vol_btn = Button(x=0, y=0,
                              label=self.volume_str(dfplayer_helper.get_volume_setting()),
                              width=self._screen_width,
                              height=self._screen_height,
                              label_font=FONT,
                              fill_color=self._background_color,
                              label_color=self._text_color,
                              label_scale=3)
        self._group.append(self.vol_btn)

        dfplayer_helper.play_track(settings.read_persistent_settings()["intro_sound_index"])
        dfplayer_helper.player.loop()

    def volume_str(self, volume):
        return str(volume) + "%"

    def up(self):
        self.vol_btn.label = self.volume_str(dfplayer_helper.louder())
        return self

    def down(self):
        self.vol_btn.label = self.volume_str(dfplayer_helper.quieter())
        return self

    def back(self):
        dfplayer_helper.player.stop()
        dfplayer_helper.save_volume_setting()
        return self.prev_screen


class BrightnessMenu(Screen):
    def __init__(self, prev_screen):
        super().__init__(prev_screen)

        self.brightness_btn = Button(x=0, y=0,
                                     label=self.brightness_str(display_helper.get_brightness_setting()),
                                     width=self._screen_width,
                                     height=self._screen_height,
                                     label_font=FONT,
                                     fill_color=self._background_color,
                                     label_color=self._text_color,
                                     label_scale=3)
        self._group.append(self.brightness_btn)

    def brightness_str(self, brightness):
        return str(brightness) + "%"

    def up(self):
        dfplayer_helper.play_ui_beep()
        self.brightness_btn.label = self.brightness_str(display_helper.brighter())
        return self

    def down(self):
        dfplayer_helper.play_ui_beep()
        self.brightness_btn.label = self.brightness_str(display_helper.dimmer())
        return self

    def back(self):
        dfplayer_helper.play_ui_beep()
        display_helper.save_setting()
        return self.prev_screen


class ListMenu(Screen):
    _menu_item_style = 1
    _menu_item_font = FONT
    _menu_item_width = Screen._screen_width
    _menu_item_height = 20
    _buttons: []
    _selected_button_indx: int
    _current_symbol = "-"

    def __init__(self, prev_screen):
        super().__init__(prev_screen)
        self._selected_button_indx = 0
        self._current_button_index = 0

    def getButtons(self, button_names):
        memu_items = []
        for n, button in enumerate(button_names):
            x = 0
            y = n * self._menu_item_height
            memu_items.append(
                Button(
                    x=x,
                    y=y,
                    label=button,
                    width=self._menu_item_width,
                    height=self._menu_item_height,
                    label_font=self._menu_item_font,
                    fill_color=self._background_color,
                    label_color=self._text_color,
                    selected_fill=self._text_color,
                    selected_label=self._background_color,
                    outline_color=self._background_color,
                    selected_outline=self._text_color,
                    style=self._menu_item_style))
        return memu_items

    def _update_offset(self, offset):
        for n, button in enumerate(self._buttons):
            button.y = self._menu_item_height * n + offset

    @property
    def _selected_button(self):
        return self._buttons[self._selected_button_indx]

    def selectItem(self, index):
        self._selected_button.selected = False
        self._buttons[index].selected = True
        self._selected_button_indx = index

    def make_current(self, index):
        curr_button = self._buttons[self._current_button_index]
        curr_button.label = self._clear_format(curr_button.label)

        self._current_button_index = index
        self._buttons[index].label = self._format_current(self._buttons[index].label)

    def _format_current(self, label):
        return "{} {} {}".format(self._current_symbol, label, self._current_symbol)

    def _clear_format(self, label):
        regex = r"{} (.*){}".format(self._current_symbol, self._current_symbol)
        search_result = re.search(regex, label)
        return label if search_result is None else search_result.group(1)

    def down(self):
        dfplayer_helper.play_ui_beep()
        if self._selected_button_indx == len(self._buttons) - 1:
            self.selectItem(0)
            if self._selected_button.y < 0:
                self._update_offset(0)
        else:
            self.selectItem(self._selected_button_indx + 1)
            offset = self._screen_height - self._selected_button.y - self._menu_item_height
            if offset < 0:
                self._update_offset(offset)
        return self

    def up(self):
        dfplayer_helper.play_ui_beep()
        if self._selected_button_indx == 0:
            self.selectItem(len(self._buttons) - 1)
            offset = self._screen_height - self._selected_button.y - self._menu_item_height
            if offset < 0:
                self._update_offset(offset)
        else:
            self.selectItem(self._selected_button_indx - 1)
            if self._selected_button.y < 0:
                self._update_offset(0)
        return self


class MainMenu(ListMenu):
    def __init__(self, prev_screen):
        super().__init__(prev_screen)
        self._menu_items = \
            [
                ["Time", ClockSettingScreen],
                ["Clock Color", UIColorMenu],
                ["Volume", VolumeMenu],
                ["Brightness", BrightnessMenu],
                ["Select Gif", GifScreen],
                ["Select Sound", IntroSoundSelectMenu]
            ]
        self._buttons = self.getButtons(map(lambda menu_item: menu_item[0], self._menu_items))
        self.selectItem(0)
        for button in self._buttons:
            self._group.append(button)

    def forward(self):
        dfplayer_helper.play_ui_beep()
        return self._menu_items[self._selected_button_indx][1](self)


class GifScreen(ListMenu):

    def __init__(self, prev_screen):
        super().__init__(prev_screen)
        self._gif_names = gif_helper.get_gif_names()
        self._gif_paths = gif_helper.get_gif_paths()
        self._current_gif_indx = gif_helper.get_intro_gif_index()
        self._buttons = self.getButtons(self._gif_names)
        self.selectItem(0)
        self.make_current(self._current_gif_indx)
        for button in self._buttons:
            self._group.append(button)

    def forward(self):
        dfplayer_helper.play_ui_beep()
        stngs = settings.read_persistent_settings()
        self.make_current(self._selected_button_indx)
        stngs["gif_file"] = self._gif_paths[self._selected_button_indx]
        settings.save_persistent_settings(stngs)
        return self


class UIColorMenu(ListMenu):
    def __init__(self, prev_screen):
        super().__init__(prev_screen)
        self._colors = \
            (
                ("white", 0xffffff),
                ("green", 0x00FF00),
                ("red", 0xFF0000),
                ("blue", 0x0000FF),
                ("orange", 0xFFA500),
                ("aqua", 0x00ffff),
                ("yellow", 0xffff00)
            )

        self._buttons = self.getButtons(self._colors)

        for button in self._buttons:
            self._group.append(button)
        self.selectItem(0)

        curr_color = settings.read_persistent_settings()["ui_text_color"]
        curr_color_index = self._colors.index(next(filter(lambda c: c[1] == curr_color, self._colors)))

        self.make_current(curr_color_index)

    def getButtons(self, colors):
        memu_items = []
        for n, color in enumerate(colors):
            x = 0
            y = n * self._menu_item_height
            memu_items.append(
                Button(
                    x=x,
                    y=y,
                    label=color[0],
                    width=self._menu_item_width,
                    height=self._menu_item_height,
                    label_font=self._menu_item_font,
                    fill_color=self._background_color,
                    label_color=color[1],
                    selected_fill=color[1],
                    selected_label=self._background_color,
                    outline_color=self._background_color,
                    selected_outline=color[1],
                    style=self._menu_item_style))
        return memu_items

    def forward(self):
        dfplayer_helper.play_ui_beep()
        stngs = settings.read_persistent_settings()
        curr_color = self._colors[self._selected_button_indx][1]
        stngs["ui_text_color"] = curr_color
        settings.save_persistent_settings(stngs)
        Screen._text_color = curr_color
        return ClockScreen()


class IntroSoundSelectMenu(ListMenu):
    def __init__(self, prev_screen):
        super().__init__(prev_screen)
        stngs = settings.read_persistent_settings()
        self._sounds = stngs["sounds"]
        curr_sound_index = stngs["intro_sound_index"]

        self._buttons = self.getButtons(self._sounds)

        for button in self._buttons:
            self._group.append(button)

        self.selectItem(0)
        self.make_current(curr_sound_index - 1)

        dfplayer_helper.play_track(1)

    def up(self):
        super().up()
        dfplayer_helper.play_track(self._selected_button_indx + 1)
        return self

    def down(self):
        super().down()
        dfplayer_helper.play_track(self._selected_button_indx + 1)
        return self

    def back(self):
        dfplayer_helper.player.stop()
        return self.prev_screen

    def forward(self):
        stngs = settings.read_persistent_settings()
        curr_sound = self._selected_button_indx + 1
        stngs["intro_sound_index"] = curr_sound
        settings.save_persistent_settings(stngs)
        self.make_current(self._selected_button_indx)
        return self
