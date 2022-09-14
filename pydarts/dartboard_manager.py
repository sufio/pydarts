import asyncio
from enum import Enum
from typing import Tuple
from multiprocessing import Queue

from bleak import BleakClient
from bleak.exc import BleakError

from backend.messaging import Messaging


ADDRESS = "58:93:d8:b8:bd:35"

# For mac
# ADDRESS = "87B0FB55-93A8-C386-A5C1-CE5AFC32202E"


class MessageType(Enum):
    STATUS = "status"
    SCORE = "score"
    QUIT = "quit"


class DartboardManager(Messaging):
    """
    Dartsboard manager
    """

    BATTERY_LEVEL_UUID = "00002A19-0000-1000-8000-00805f9b34fb"
    SCORE_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
    NOTIFY_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

    def __init__(self, address, q_in: Queue, q_out: Queue) -> None:
        super().__init__(q_in, q_out)

        self.address = address

        self.client: BleakClient = None

    async def enable_notifications(self) -> None:
        """
        Setup dartboard to send dart score notification
        """
        await self.client.write_gatt_char(self.NOTIFY_UUID, bytearray([0x03]))
        await self.client.start_notify(
            self.SCORE_UUID, self.dart_score, response=True
        )

    async def disable_notifications(self) -> None:
        """
        Setup dartboadr to NOT send dart score notificaitons
        """
        await self.client.write_gatt_char(self.NOTIFY_UUID, bytearray([0x02]))
        await self.client.stop_notify(self.SCORE_UUID)

    async def __aenter__(self) -> "DartboardManager":
        self.client = await BleakClient(self.address).__aenter__()
        self.client.set_disconnected_callback(self.disconnected_callback)
        await self.enable_notifications()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disable_notifications()
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_status(self) -> Tuple[bool, int]:
        """
        Get bluetooth connection status + battery status of dartboard
        """
        status = (False, None)
        if self.client.is_connected:
            battery_level = await self.client.read_gatt_char(
                self.BATTERY_LEVEL_UUID
            )
            status = (True, int(battery_level[0]))
        self._send_message(MessageType.STATUS.value, status)

    async def reconnect(self) -> None:
        await self.client.connect()
        await self.enable_notifications()

    def disconnected_callback(self, _) -> None:
        """
        Unsolicited disconnect event
        """
        status = (False, None)
        self._send_message(MessageType.STATUS.value, status)

    def dart_score(self, _, data) -> None:
        """
        Dart score
        """
        if not self.client.is_connected:
            return
        if not isinstance(data, bytearray) or len(data) < 2:
            return

        dart_score = int(data[0])
        dart_multiplier = int(data[1]) if data[1] else 1
        final_score = dart_score * dart_multiplier

        if final_score > 60:
            return

        self._send_message(MessageType.SCORE.value, final_score)


async def amain(address, q_in, q_out):
    should_run = True
    async with DartboardManager(address, q_in, q_out) as client:
        while should_run:
            while msg := client._recv_message():
                if msg["type"] == MessageType.STATUS.value:
                    await client.get_status()
                elif msg["type"] == MessageType.QUIT.value:
                    should_run = False
                    break
            if not client.client.is_connected:
                try:
                    await client.reconnect()
                except BleakError:
                    await asyncio.sleep(1)
                except Exception:
                    await asyncio.sleep(1)
            await asyncio.sleep(0.5)


def run(q_in, q_out, address=None):
    try:
        asyncio.run(
            amain(
                address if address else ADDRESS,
                q_in,
                q_out,
            )
        )
    except Exception as e:
        print("Exiting...: {}".format(e))
    except KeyboardInterrupt:
        print("Exiting... keyboard")


if __name__ == "__main__":
    run(Queue(), Queue())
