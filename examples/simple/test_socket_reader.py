from dingus import Dingus

from socket_reader import read_socket


class TestSocketReader:
    def setup(self):
        self.socket = Dingus()
        self.data_that_was_read = read_socket(self.socket)

    def should_read_from_socket(self):
        assert self.socket.calls('recv', 1024).once()

    def should_return_what_is_read(self):
        assert self.data_that_was_read == self.socket.recv()

    def should_close_socket_after_reading(self):
        # Sequence tests like this often aren't needed, as your higher-level
        # system tests will catch such problems. But I include one here to
        # illustrate more complex use of the "calls" list.

        assert self.socket.calls('close')
        call_names = [call.name for call in self.socket.calls]
        assert call_names.index('close') > call_names.index('recv')

