import multiprocessing as mp
from time import sleep
from typing import Optional

from player import Player
from messaging import Messaging
from dartboard_manager import run, MessageType


class DartboardClient(Messaging):
    """
    Dartboard client
    """

    def __init__(self) -> None:
        super().__init__(mp.Queue(), mp.Queue())

        self.proc: Optional[mp.Process] = None
        self.player: Player = Player()

    def __enter__(self) -> "DartboardClient":
        self.connect_darts()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.send_quit()
        self.proc.join()

    def connect_darts(self) -> None:
        self.proc = mp.Process(
            target=run, args=(self.q_out, self.q_in), daemon=True
        )
        self.proc.start()

    def process_messages(self) -> None:
        if not self.proc.is_alive():
            return
        while msg := self._recv_message():
            if msg["type"] == MessageType.STATUS.value:
                is_connected, battery = msg["data"]
                print("[STATUS] {} : {}".format(is_connected, battery))
            elif msg["type"] == MessageType.SCORE.value:
                if self.player.finished:
                    self.player = Player()
                self.player.score = msg["data"]
                print("[PLAYER] {}".format(self.player))

    def get_status(self) -> None:
        if self.proc.is_alive():
            self._send_message(MessageType.STATUS.value, "")

    def send_quit(self) -> None:
        if self.proc.is_alive():
            self._send_message(MessageType.QUIT.value, "")


def main():
    client = DartboardClient()
    should_run = True
    while should_run:
        try:
            client.process_messages()
            sleep(1)
        except KeyboardInterrupt:
            should_run = False


if __name__ == "__main__":
    main()
