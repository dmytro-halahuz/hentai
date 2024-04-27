# SPDX-FileCopyrightText: 2022 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_button.button`
================================================================================

Bitmap 3x3 Spritesheet based UI Button for displayio


* Author(s): Tim Cocks

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
from adafruit_imageload.tilegrid_inflator import inflate_tilegrid
from adafruit_imageload import load
from adafruit_button.button_base import ButtonBase


class SpriteButton(ButtonBase):
    """Helper class for creating 3x3 Bitmap Spritesheet UI buttons for ``displayio``.

    :param x: The x position of the button.
    :param y: The y position of the button.
    :param width: The width of the button in tiles.
    :param height: The height of the button in tiles.
    :param name: A name, or miscellaneous string that is stored on the button.
    :param label: The text that appears inside the button. Defaults to not displaying the label.
    :param label_font: The button label font.
    :param label_color: The color of the button label text. Defaults to 0x0.
    :param selected_label: Text that appears when selected
    :param string bmp_path: The path of the 3x3 spritesheet Bitmap file
    :param string selected_bmp_path: The path of the 3x3 spritesheet Bitmap file to use when pressed
    :param int or tuple transparent_index: Index(s) that will be made transparent on the Palette
    """

    def __init__(
        self,
        *,
        x,
        y,
        width,
        height,
        name=None,
        label=None,
        label_font=None,
        label_color=0x0,
        selected_label=None,
        bmp_path=None,
        selected_bmp_path=None,
        transparent_index=None,
        label_scale=None
    ):
        if bmp_path is None:
            raise ValueError("Please supply bmp_path. It cannot be None.")

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            name=name,
            label=label,
            label_font=label_font,
            label_color=label_color,
            selected_label=selected_label,
            label_scale=label_scale,
        )

        self._bmp, self._bmp_palette = load(bmp_path)

        self._selected_bmp = None
        self._selected_bmp_palette = None
        self._selected = False

        if selected_bmp_path is not None:
            self._selected_bmp, self._selected_bmp_palette = load(selected_bmp_path)
            if transparent_index is not None:
                if isinstance(transparent_index, tuple):
                    for _index in transparent_index:
                        self._selected_bmp_palette.make_transparent(_index)
                elif isinstance(transparent_index, int):
                    self._selected_bmp_palette.make_transparent(0)

        self._btn_tilegrid = inflate_tilegrid(
            bmp_obj=self._bmp,
            bmp_palette=self._bmp_palette,
            target_size=(
                width // (self._bmp.width // 3),
                height // (self._bmp.height // 3),
            ),
            transparent_index=transparent_index,
        )
        self.append(self._btn_tilegrid)

        self.label = label

    @property
    def width(self):
        """The width of the button"""
        return self._width

    @property
    def height(self):
        """The height of the button"""
        return self._height

    def contains(self, point):
        """Used to determine if a point is contained within a button. For example,
        ``button.contains(touch)`` where ``touch`` is the touch point on the screen will allow for
        determining that a button has been touched.
        """
        return (self.x <= point[0] <= self.x + self.width) and (
            self.y <= point[1] <= self.y + self.height
        )

    def _subclass_selected_behavior(self, value):
        if self._selected:
            if self._selected_bmp is not None:
                self._btn_tilegrid.bitmap = self._selected_bmp
                self._btn_tilegrid.pixel_shader = self._selected_bmp_palette
        else:
            self._btn_tilegrid.bitmap = self._bmp
            self._btn_tilegrid.pixel_shader = self._bmp_palette
