from adafruit_button import Button
from terminalio import FONT

class Menu:
    menu_item_width = 128
    menu_item_height = 20

    menu_item_fill_color = 0x000000
    menu_item_text_color = 0xFFFFFF
    menu_item_style = 1
    menu_item_font = FONT

    def __init__(self):
        self.menu_items = []
        self.selected_item = 0

    def selectItem(self, index):
        self.menu_items[self.selected_item].selected = False
        self.menu_items[index].selected = True
        self.selected_item = index

    def down(self):
        if self.selected_item == len(self.menu_items) -1:
            self.selectItem(0)
        else:
            self.selectItem(self.selected_item + 1)

    def up(self):
        if self.selected_item == 0:
            self.selectItem(len(self.menu_items) -1)
        else:
            self.selectItem(self.selected_item - 1)

    def _getMenuItems(self, menu_item_names):
        memu_items = []
        for n, button in enumerate(menu_item_names):
            x = 0
            y = n * self.menu_item_height
            memu_items.append(
                Button(
                    x=x,
                    y=y,
                    label=button,
                    width=self.menu_item_width,
                    height=self.menu_item_height,
                    label_font=self.menu_item_font,
                    fill_color=self.menu_item_fill_color,
                    label_color=self.menu_item_text_color,
                    style=self.menu_item_style))
        return memu_items

class MainMenu(Menu):
    menu_item_names = [
        "Volume",
        "Brightness",
        "Select Gif",
        "Select Sound"
    ]

    def __init__(self):
        super().__init__()

        self.menu_items = self._getMenuItems(self.menu_item_names)
        self.selectItem(0)

