from enum import Enum
from typing import Any, Mapping, NamedTuple

from rpm_metadata_parser.bytebuf import ByteBuf
from rpm_metadata_parser.errors import RpmParsingError

type Tag = int


class HeaderIndex(NamedTuple):
    number_of_entities: int
    section_size: int


class EntryType(Enum):
    NULL = 0
    CHAR = 1
    INT8 = 2
    INT16 = 3
    INT32 = 4
    INT64 = 5
    STRING = 6
    BIN = 7
    STRING_ARRAY = 8
    I18_STRING = 9


class Header(NamedTuple):
    index: HeaderIndex
    entries: Mapping[Tag, Any]

    @property
    def padding(self) -> int:
        """Calculate section padding."""
        return (8 - (self.index.section_size % 8)) % 8


def parse_header(buffer: ByteBuf) -> Header:
    index = _parse_header_index(buffer)
    entries = {}

    begin_entries_section_offset = buffer.offset
    begin_entries_data_offset = (
        begin_entries_section_offset + index.number_of_entities * 16
    )

    for i in range(index.number_of_entities):
        buffer.offset = begin_entries_section_offset + i * 16

        tag = buffer.read_uint()
        kind = EntryType(buffer.read_uint())
        offset = buffer.read_uint()
        count = buffer.read_uint()

        buffer.offset = begin_entries_data_offset + offset
        value = _parse_entry_data(buffer, kind, count)

        entries[tag] = value

    buffer.offset = begin_entries_data_offset + index.section_size

    return Header(index, entries)


def _parse_header_index(buffer: ByteBuf) -> HeaderIndex:
    buffer.assert_bytes(b"\x8e\xad\xe8\x01")
    buffer.skip(4)  # reserved

    number_of_entities = buffer.read_uint()
    section_size = buffer.read_uint()

    return HeaderIndex(number_of_entities, section_size)


def _parse_entry_data(buffer: ByteBuf, kind: EntryType, count: int) -> Any:
    match kind:
        case EntryType.BIN:
            return buffer.take(count)
        case EntryType.STRING | EntryType.I18_STRING:
            return buffer.read_null_terminate_string()
        case EntryType.STRING_ARRAY:
            return [buffer.read_null_terminate_string() for _ in range(count)]
        case EntryType.INT32:
            if count > 1:
                return buffer.read_array(buffer.read_uint, count)
            return buffer.read_uint()
        case EntryType.INT16:
            if count > 1:
                return buffer.read_array(buffer.read_ushort, count)
            return buffer.read_ushort()
        case EntryType.INT8:
            if count > 1:
                return buffer.read_array(buffer.read_byte, count)
            return buffer.read_byte()
        case EntryType.NULL:
            return None
        case EntryType.INT64:
            raise RpmParsingError("Unsupported INT64 type fo entry's value!")

    raise RpmParsingError(f"Unknown entry's type: {kind}!")
