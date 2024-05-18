import struct
from typing import IO, Callable

from rpm_metadata_parser.errors import RpmParsingError


class ByteBuf:
    def __init__(self, stream: IO[bytes]):
        self._stream = stream

    def assert_bytes(self, expected: bytes):
        actual_bytes = self._stream.read(len(expected))
        if actual_bytes != expected:
            raise RpmParsingError(
                "Failed to assert:"
                f" expected {repr(expected)}, but got {repr(actual_bytes)}"
            )

    def read_null_terminate_string(self) -> str:
        start_offset = self.offset

        while self._stream.read(1)[0] != 0:
            pass

        length = self.offset - start_offset
        self.offset = start_offset

        string = self._stream.read(length - 1).decode("utf-8")
        self.skip(1)  # eat '\0'

        return string

    def read_uint(self) -> int:
        return struct.unpack(">I", self._stream.read(4))[0]

    def read_ushort(self) -> int:
        return struct.unpack(">H", self._stream.read(2))[0]

    def read_byte(self) -> int:
        return self._stream.read(1)[0]

    def skip(self, n: int):
        self._stream.seek(self.offset + n)

    def take(self, n: int):
        return self._stream.read(n)

    def read_array[T](self, reader: Callable[[], T], n: int) -> list[T]:
        return [reader() for _ in range(n)]

    def read_all(self) -> bytes:
        return self._stream.read()

    @property
    def offset(self) -> int:
        return self._stream.tell()

    @offset.setter
    def offset(self, offset: int):
        self._stream.seek(offset)
