import glob

import requests
from requests.auth import HTTPDigestAuth

headers = {"Content-Type": "text/xml"}
for xml_file in glob.iglob("/path/to/xml/files/*.xml"):
    xml_file = {"file": open(xml_file, "rb")}
    r = requests.post(
        "https://climmob.net/[climmob_user]/push",
        auth=HTTPDigestAuth("[data_collector]", "[password]"),
        files=xml_file,
    )
    print("File pushed {} with status {}".format(xml_file, r.status_code))
