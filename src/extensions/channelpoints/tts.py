from dataclasses import dataclass
from gtts import gTTS
from ...core.twitch import ChannelPointRedemption


@dataclass
class ScuffedTTSUpdate:
    timestamp: str
    username: str
    text: str
    audio_file: str  # always the same for the same client


class ScuffedTTS:
    def __init__(self, redemption_title: str, logfile: str, audiofile: str):
        self.redemption_title = redemption_title
        self.logfile = logfile
        self.audiofile = audiofile
        self.listeners = []
        self.latest = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def handle_redemption(self, red: ChannelPointRedemption):
        if red.reward_name != self.redemption_title:
            return
        print(f"[TTS] {red.user_name} says: {red.user_input}")
        tts = gTTS(red.user_input)

        tts.save(self.audiofile)
        with open(self.logfile, "a") as f:
            f.write(f"{red.timestamp} {red.user_name} {red.user_input}")

        update = ScuffedTTSUpdate(
            red.timestamp, red.user_name, red.user_input, self.audiofile
        )

        self.latest.append(update)

        for listener in self.listeners:
            listener(update)

    def get_latest_fifo(self):
        if len(self.latest) < 1:
            return None
        return self.latest.pop(0)
