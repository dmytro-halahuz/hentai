# SPDX-FileCopyrightText: 2022 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_button.button`
================================================================================

UI Buttons for displayio


* Author(s): Limor Fried

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
from adafruit_display_text.bitmap_label import Label
from displayio import Group


def _check_color(color):
    # if a tuple is supplied, convert it to a RGB number
    if isinstance(color, tuple):
        r, g, b = color
        return int((r << 16) + (g << 8) + (b & 0xFF))
    return color


class ButtonBase(Group):
    # pylint: disable=too-many-instance-attributes
    """Superclass for creating UI buttons for ``displayio``.

    :param x: The x position of the button.
    :param y: The y position of the button.
    :param width: The width of the button in tiles.
    :param height: The height of the button in tiles.
    :param name: A name, or miscellaneous string that is stored on the button.
    :param label: The text that appears inside the button. Defaults to not displaying the label.
    :param label_font: The button label font.
    :param label_color: The color of the button label text. Defaults to 0x0.
    :param selected_label: Text that appears when selected
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
        label_scale=None
    ):
        super().__init__(x=x, y=y)
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self._font = label_font
        self._selected = False
        self.name = name
        self._label = label
        self._label_color = label_color
        self._label_font = label_font
        self._selected_label = _check_color(selected_label)
        self._label_scale = label_scale or 1

    @property
    def label(self):
        """The text label of the button"""
        return self._label.text

    @label.setter
    def label(self, newtext):
        if self._label and self and (self[-1] == self._label):
            self.pop()

        self._label = None
        if not newtext or (self._label_color is None):  # no new text
            return  # nothing to do!

        if not self._label_font:
            raise RuntimeError("Please provide label font")
        self._label = Label(self._label_font, text=newtext, scale=self._label_scale)
        dims = list(self._label.bounding_box)
        dims[2] *= self._label.scale
        dims[3] *= self._label.scale
        if dims[2] >= self.width or dims[3] >= self.height:
            while len(self._label.text) > 1 and (
                dims[2] >= self.width or dims[3] >= self.height
            ):
                self._label.text = "{}.".format(self._label.text[:-2])
                dims = list(self._label.bounding_box)
                dims[2] *= self._label.scale
                dims[3] *= self._label.scale
            if len(self._label.text) <= 1:
                raise RuntimeError("Button not large enough for label")
        self._label.x = (self.width - dims[2]) // 2
        self._label.y = self.height // 2
        self._label.color = (
            self._label_color if not self.selected else self._selected_label
        )
        self.append(self._label)

        if (self.selected_label is None) and (self._label_color is not None):
            self.selected_label = (~self._label_color) & 0xFFFFFF

    def _subclass_selected_behavior(self, value):
        # Subclasses should overide this!
        pass

    @property
    def selected(self):
        """Selected inverts the colors."""
        return self._selected

    @selected.setter
    def selected(self, value):
        if value == self._selected:
            return  # bail now, nothing more to do
        self._selected = value

        if self._selected:
            new_label = self.selected_label
        else:
            new_label = self._label_color
        if self._label is not None:
            self._label.color = new_label

        self._subclass_selected_behavior(value)

    @property
    def selected_label(self):
        """The font color of the button when selected"""
        return self._selected_label

    @selected_label.setter
    def selected_label(self, new_color):
        self._selected_label = _check_color(new_color)

    @property
    def label_color(self):
        """The font color of the button"""
        return self._label_color

    @label_color.setter
    def label_color(self, new_color):
        self._label_color = _check_color(new_color)
        self._label.color = self._label_color
