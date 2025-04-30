from dataclasses import dataclass
import socket
import threading


@dataclass
class TwitchIRCSettings:
    hostname: str
    port: int
    bot_nick: str
    channel: str


@dataclass
class TwitchIRCMessage:
    sender: str
    content: str


class TwitchIRCClient:
    def __init__(self, settings: TwitchIRCSettings):
        self.settings = settings
        self.sock = None
        self.listen_thread = None

    def connect(self, access_token: str):

        print("[IRC] Connecting...")

        sock = socket.socket()
        sock.connect((self.settings.hostname, self.settings.port))
        sock.send(f"PASS oauth:{access_token}\r\n".encode("utf-8"))
        sock.send(f"NICK {self.settings.bot_nick}\r\n".encode("utf-8"))
        sock.send(f"JOIN #{self.settings.channel}\r\n".encode("utf-8"))
        self.sock = sock

        print("[IRC] Connected.")

    def send_message_to_chat(self, content: str):
        if self.sock is None:
            print("[IRC] Can't send message because client is not connected.")
            return
        response = f"PRIVMSG #{self.settings.channel} :{content}\r\n"
        self.sock.send(response.encode("utf-8"))

    def listen_to_chat(self, handle_message, daemon: bool = True):

        if self.sock is None:
            print("[IRC] Can't listen to chat because client is not connected.")
            return
        if self.listen_thread is not None:
            print("[IRC] Already listening to chat.")
            return

        def listen_handler():
            while True:
                resp = self.sock.recv(2048).decode("utf-8")
                if resp.startswith("PING"):
                    self.sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                elif "PRIVMSG" in resp:
                    # print(resp)
                    username = resp.split("!", 1)[0][1:]
                    message = resp.split("PRIVMSG", 1)[1].split(":", 1)[1]
                    handle_message(TwitchIRCMessage(username, message))

        self.listen_thread = threading.Thread(target=listen_handler)
        self.listen_thread.setDaemon(daemon)
        self.listen_thread.start()
