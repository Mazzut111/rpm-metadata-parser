from enum import Enum


class InfoTag(Enum):
    Name = 1000
    Version = 1001
    Release = 1002
    Summery = 1004
    Description = 1005
    Size = 1009
    Distribution = 1010
    Vendor = 1011
    License = 1014
    Packager = 1015
    Group = 1016
    Url = 1020
    Os = 1021
    Arch = 1022
    SourceRpm = 1044
    ArchiveSize = 1046
    RpmVersion = 10064
    Cookie = 1094
    DistUrl = 1123
    PayloadFormat = 1124
    PayloadCompressor = 1125
    PayloadFlags = 1126
