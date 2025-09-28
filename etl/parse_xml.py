import xml.etree.ElementTree as ET
import json

tree = ET.parse("data/raw/momo.xml")
root = tree.getroot()

d = {}
d[root.tag] = []

for child in root:
    attribs = child.attrib
    new_dict = {
        "protocol": attribs["protocol"],
        "address": attribs["protocol"],
        "date": attribs["date"],
        "type": attribs["type"],
        "subject": attribs["subject"],
        "body": attribs["body"],
        "toa": attribs["toa"],
        "sc_toa": attribs["sc_toa"],
        "service_center": attribs["service_center"],
        "read": attribs["read"],
        "status": attribs["status"],
        "locked": attribs["protocol"],
        "date_sent": attribs["date_sent"],
        "sub_id": attribs["sub_id"],
        "readable_date": attribs["readable_date"],
        "contact_name": attribs["contact_name"]
    }

    d[root.tag].append(new_dict)

with open("data.json", "w") as json_file:
    json.dump(d, json_file)

print(d)
