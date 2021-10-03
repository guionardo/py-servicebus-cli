import time

from azure.servicebus.management import ServiceBusAdministrationClient


class QueueInfo:

    def __init__(self, connection_string: str, queue_name: str,
                 dead_letter: bool = False):
        self._cs = connection_string
        self._queue_name = queue_name
        self._dead_letter = dead_letter
        self._runtime_properties = None
        self._last_runtime_properties = 0

    def _get_runtime_properties(self):
        if self._runtime_properties and \
                time.time()-self._last_runtime_properties < 15:
            return
        with ServiceBusAdministrationClient.from_connection_string(self._cs) \
                as manager:
            self._runtime_properties = manager.get_queue_runtime_properties(
                self._queue_name)
            self._last_runtime_properties = time.time()

    @property
    def active_message_count(self) -> int:
        self._get_runtime_properties()
        return self._runtime_properties.active_message_count

    @property
    def total_message_count(self) -> int:
        self._get_runtime_properties()
        return self._runtime_properties.total_message_count

    @property
    def dead_letter_message_count(self) -> int:
        self._get_runtime_properties()
        return self._runtime_properties.dead_letter_message_count

    @property
    def size_in_bytes(self) -> int:
        self._get_runtime_properties()
        return self._runtime_properties.size_in_bytes
