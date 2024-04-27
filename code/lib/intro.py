import settings
from hardware_helpers import display_helper, dfplayer_helper, gif_helper
import gifio
import time
import struct

def playIntro():
    stngs = settings.read_persistent_settings()

    display = display_helper.display
    odg = gifio.OnDiskGif(stngs["gif_file"])

    mp3_index = stngs["intro_sound_index"]
    dfplayer_helper.play_track(mp3_index)

    gif_helper.play_gif(odg)
