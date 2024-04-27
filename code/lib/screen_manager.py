import screen
from hardware_helpers import btn_helper

class ScreenManager:
    def __init__(self):
        self._current_screen = screen.ClockScreen()

    def show(self):
        btn_helper.read_buttons()

        if btn_helper.up_btn.fell:
            self._current_screen = self._current_screen.up()
        elif btn_helper.down_btn.fell:
            self._current_screen = self._current_screen.down()
        elif btn_helper.fwd_btn.fell:
            self._current_screen = self._current_screen.forward()
        elif btn_helper.back_btn.fell:
            self._current_screen = self._current_screen.back()

        self._current_screen.show()