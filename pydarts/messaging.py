from queue import Empty
from multiprocessing import Queue


class Messaging:
    """
    Allows 2-way communication via queues
    """

    def __init__(self, q_in: Queue, q_out: Queue) -> None:
        self.q_in = q_in
        self.q_out = q_out

    def _send_message(self, type, data):
        if not self.q_out:
            raise Exception("output Queue is dead!")

        self.q_out.put({"type": type, "data": data})

    def _recv_message(self):
        try:
            data = self.q_in.get_nowait()
        except Empty:
            data = None
        return data
