from typing import IO, NamedTuple, Optional

from rpm_metadata_parser.bytebuf import ByteBuf
from rpm_metadata_parser.header import Header, parse_header
from rpm_metadata_parser.lead import Lead, parse_lead
from rpm_metadata_parser.tags import InfoTag


class RpmPackage(NamedTuple):
    raw: "RawPackage"

    @property
    def name(self) -> str:
        return self.raw.header.entries[1000]

    @property
    def os(self) -> str:
        return self.raw.header.entries[InfoTag.Os.value]

    @property
    def release(self) -> str:
        return self.raw.header.entries[InfoTag.Version.value]

    @property
    def version(self) -> str:
        return self.raw.header.entries[InfoTag.Release.value]

    @property
    def summery(self) -> str:
        return self.raw.header.entries[InfoTag.Summery.value]

    @property
    def description(self) -> str:
        return self.raw.header.entries[InfoTag.Description.value]

    @property
    def size(self) -> str:
        return self.raw.header.entries[InfoTag.Size.value]

    @property
    def distribution(self) -> str:
        return self.raw.header.entries[InfoTag.Distribution.value]


class RawPackage(NamedTuple):
    lead: Lead
    signature: Header
    header: Header
    payload: Optional[bytes]


def parse(stream: IO[bytes], *, capture_payload=False) -> RpmPackage:
    buffer = ByteBuf(stream)

    lead = parse_lead(buffer)

    signature = parse_header(buffer)
    buffer.skip(signature.padding)

    header = parse_header(buffer)

    # fix: read by size from signature record
    payload = buffer.read_all() if capture_payload else None

    return RpmPackage(RawPackage(lead, signature, header, payload))
