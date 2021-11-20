import json
import platform

import requests

from src.util import get_version


def get_mac():
    import uuid
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    mac_address = '-'.join([mac_address[i:i + 2] for i in range(0, 11, 2)])
    return mac_address


def check_newest():
    data = {
        "app": {
            "name": "my_dict",
            "version": get_version(),
            "md5sum": "",
            "statistics": {}
        },
        "host": {
            "os": platform.system(),
            "mac": get_mac(),
            "ext": {
                "uname": platform.uname(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
            }
        }
    }

    try:
        response = requests.post("http://home.mydata.top:8681/api/my_dict/check_newest", data=json.dumps(data))
        print(response.text)
        res = response.json()
        if res["result"]["code"] != 0 or "new_version" not in res:
            return False, None
        new_version = res["info"]
        return True, new_version
    except:
        return False, None
