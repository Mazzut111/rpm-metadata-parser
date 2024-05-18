from enum import Enum
from typing import NamedTuple, Tuple

from rpm_metadata_parser.bytebuf import ByteBuf
from rpm_metadata_parser.errors import RpmParsingError


class PackageType(Enum):
    BINARY = "BINARY"
    SOURCE = "SOURCE"


class Lead(NamedTuple):
    """Partial RPM Lead structure representation."""

    version: Tuple[int, int]
    """RPM package format version. Values: `(major, minor)`."""

    kind: PackageType

    # dropped:
    # - arch_num
    # - name
    # - os_num
    # - signature_type


def parse_lead(buffer: ByteBuf) -> Lead:
    buffer.assert_bytes(b"\xed\xab\xee\xdb")

    major = buffer.read_byte()
    minor = buffer.read_byte()

    kind = _parse_package_type(buffer)

    # skip some deprecated fields
    buffer.skip(2 + 66 + 2 + 2 + 16)

    return Lead(version=(major, minor), kind=kind)


def _parse_package_type(buffer: ByteBuf) -> PackageType:
    value = buffer.read_ushort()

    if value == 0:
        return PackageType.BINARY
    elif value == 1:
        return PackageType.SOURCE

    raise RpmParsingError(
        f"Invalid package type value. Expected 0 (binary) or 1 (source) but got '{value}'"
    )
