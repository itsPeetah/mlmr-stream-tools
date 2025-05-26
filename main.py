from flask import jsonify, request
from flask_socketio import emit, send

from src.core.twitch import TwitchRig, TwitchRigSettings
from src.core.twitch.lib import *
from src.extensions import ChannelPoints
from main__settings import *

twitch_rig = TwitchRig(
    TwitchRigSettings(
        twitch_auth_settings=auth_settings,
        twitch_irc_settings=irc_settings,
        twitch_api_settings=api_settings,
        twitch_eventsub_settings=eventsub_settings,
    )
)

## TWITCH HANDLERS ##

bounties = ChannelPoints.bounties.BountyTracker(
    "In-Game Bounty", "BOUNTY", "./tmp/bounties.tsv"
)
bans = ChannelPoints.bounties.BountyTracker("In-Game Ban", "BAN", "./tmp/bans.tsv")
tts = ChannelPoints.tts.ScuffedTTS(
    "TTS Message", "./tmp/ttslog.tsv", "./tmp/latest.mp3"
)


@twitch_rig.irc_client.on_message()
def on_chat_msg(msg: TwitchIrc.IRCMessage):
    print(f"Message from {msg.sender}: {msg.content}---")


@twitch_rig.irc_client.on_command("!hi")
def on_hi_command(msg: TwitchIrc.IRCMessage):
    print(f"Command from {msg.sender}: {msg.content}---")
    twitch_rig.irc_client.send_message_to_chat(f"Hello, {msg.sender}!")


@twitch_rig.eventsub_client.channel_point_redemption("In-Game Bounty")
def handle_bounties(redemption: TwitchEventSub.ChannelPointRedemption):
    bounties.handle_redemption(redemption)


@twitch_rig.eventsub_client.channel_point_redemption("In-Game Ban")
def handle_bans(redemption: TwitchEventSub.ChannelPointRedemption):
    bans.handle_redemption(redemption)


@twitch_rig.eventsub_client.channel_point_redemption("TTS Message")
def handle_tts(redemption: TwitchEventSub.ChannelPointRedemption):
    tts.handle_redemption(redemption)


## MAIN ##


def main():
    twitch_rig.start()


if __name__ == "__main__":
    main()
