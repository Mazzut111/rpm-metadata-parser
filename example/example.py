import rpm_metadata_parser as rpm

with open("ruby-3.3.1-7.fc40.x86_64.rpm", "rb") as rpm_file:
    rpm_package = rpm.parse(rpm_file)

print(rpm_package)