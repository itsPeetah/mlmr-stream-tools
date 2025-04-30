from ..twitch import ChannelPointRedemption


class BountyTracker:
    def __init__(self, redemption_title: str, prefix: str, filepath: str):
        self.redemption_title = redemption_title
        self.prefix = prefix
        self.filepath = filepath

    def handle_redemption(self, red: ChannelPointRedemption):
        if red.reward_name != self.redemption_title:
            return

        print(
            f"[BOUNTIES] In-game bounty redeemed by {red.user_name}: {red.user_input}"
        )

        with open(self.filepath, "a") as f:
            f.write(
                f"{self.prefix}\t{red.user_input}\t{red.user_name}\t{red.timestamp}\n\n"
            )

    def get_bounties(self):
        results = []
        with open(self.filepath, "r") as f:
            text = f.read().strip()
            results = text.split("\n\n")
        return results
