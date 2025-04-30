import asyncio
from dataclasses import dataclass
import json

import requests
import websockets


@dataclass
class TwitchEventSubSettings:
    client_id: str
    eventsub_ws_url: str


@dataclass
class ChannelPointRedemption:
    user_name: str
    user_id: str
    user_input: str
    reward_name: str
    reward_id: str
    reward_cost: str
    timestamp: str


class TwitchEventSubClient:
    def __init__(self, settings: TwitchEventSubSettings):
        self.settings = settings
        self.stop_queued = False
        self.listeners = {}

    def _subscribe_channel_point_redemptions(
        self, session_id, access_token, broadcaster_id
    ):
        url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        headers = {
            "Client-ID": self.settings.client_id,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "type": "channel.channel_points_custom_reward_redemption.add",
            "version": "1",
            "condition": {"broadcaster_user_id": broadcaster_id},
            "transport": {"method": "websocket", "session_id": session_id},
        }

        r = requests.post(url, headers=headers, json=payload)
        return r.json()["data"][0]["id"]

    def add_channel_point_redemption_listener(self, listener):
        self.listeners["channel.channel_points_custom_reward_redemption.add"] = listener

    def run(self, access_token: str, broadcaster_id: str):
        op = asyncio.run(self._handle_eventsub_ws(access_token, broadcaster_id))
        return op

    async def _handle_eventsub_ws(self, access_token: str, broadcaster_id: str):
        async with websockets.connect(self.settings.eventsub_ws_url) as ws:
            # Step 1: Get session_id from welcome message
            print("[EventSub] Connecting...")
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            session_id = welcome_data["payload"]["session"]["id"]
            # print(f"[EventSub] Connected with session_id: {session_id}")
            print("[EventSub] Connected.")

            # Step 2: Send subscription for redemptions
            self._subscribe_channel_point_redemptions(
                session_id, access_token, broadcaster_id
            )

            # Step 3: Listen for events
            while not self.stop_queued:
                msg = await ws.recv()
                data = json.loads(msg)

                if data["metadata"]["message_type"] == "notification":
                    self._handle_subscription_notification(data)
                elif data["metadata"]["message_type"] == "session_keepalive":
                    # print("[EventSub] Keepalive received")
                    pass

    def _handle_subscription_notification(self, data: dict):
        sub_type = data["metadata"]["subscription_type"]
        event = data["payload"]["event"]
        match sub_type:
            case "channel.channel_points_custom_reward_redemption.add":
                print(
                    f"[EventSub] [Channel Points] {event['user_name']} redeemed {event['reward']['title']}"
                )
                self.listeners[sub_type](
                    ChannelPointRedemption(
                        user_name=event["user_name"],
                        user_id=event["user_id"],
                        user_input=event["user_input"],
                        reward_name=event["reward"]["title"],
                        reward_id=event["reward"]["id"],
                        reward_cost=event["reward"]["cost"],
                        timestamp=event["redeemed_at"],
                    )
                )
