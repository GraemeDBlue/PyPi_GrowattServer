"""
Example script for MIN/TLX Growatt inverters using the public API.

This script demonstrates controlling a MID/TLX Growatt
(MID-30KTL3-XH + APX battery) system.
You can obtain an API token from the Growatt API documentation or
developer portal.
"""

import json
from pathlib import Path

import requests

from . import growattServer

# Test token from official API docs
# https://www.showdoc.com.cn/262556420217021/1494053950115877
api_token = "6eb6f069523055a339d71e5b1f6c88cc"  # noqa: S105

try:
    # Initialize the API with token instead of using login
    api = growattServer.OpenApiV1(token=api_token)

    # Plant info
    plants = api.plant_list()
    print(f"Plants: Found {plants['count']} plants")  # noqa: T201
    plant_id = plants["plants"][0]["plant_id"]

    # Devices
    devices = api.device_list(plant_id)

    for device in devices["devices"]:
        print(device)  # noqa: T201
        if device["device_type"] == growattServer.DeviceType.MIN_TLX.value:
            inverter_sn = device["device_sn"]
            device_type = device["device_type"]
            print(f"Processing {device_type.name} inverter: {inverter_sn}")  # noqa: T201

            # Get device details
            inverter_data = api.min_detail(
                device_sn=inverter_sn,
            )
            print("Saving inverter data to inverter_data.json")  # noqa: T201
            with Path("inverter_data.json").open("w") as f:
                json.dump(inverter_data, f, indent=4, sort_keys=True)

            # Get energy data
            energy_data = api.min_energy(
                device_sn=inverter_sn,
            )
            print("Saving energy data to energy_data.json")  # noqa: T201
            with Path("energy_data.json").open("w") as f:
                json.dump(energy_data, f, indent=4, sort_keys=True)

            # Get energy history
            energy_history_data = api.min_energy_history(
                device_sn=inverter_sn,
            )
            print("Saving energy history data to energy_history.json")  # noqa: T201
            with Path("energy_history.json").open("w") as f:
                json.dump(
                    energy_history_data.get("datas", []),
                    f,
                    indent=4,
                    sort_keys=True,
                )

            # Get settings
            settings_data = api.min_settings(
                device_sn=inverter_sn,
            )
            print("Saving settings data to settings_data.json")  # noqa: T201
            with Path("settings_data.json").open("w") as f:
                json.dump(settings_data, f, indent=4, sort_keys=True)

            # Read time segments
            tou = api.read_time_segments(
                device_sn=inverter_sn,
                device_type=device_type,
                settings_data=settings_data,
            )
            print("Time-of-Use Segments:")  # noqa: T201
            with Path("tou_data.json").open("w") as f:
                json.dump(tou, f, indent=4, sort_keys=True)

            # Read discharge power
            discharge_power = api.common_read_parameter(
                device_sn=inverter_sn,
                device_type=device_type,
                parameter_id="discharge_power",
            )
            print(f"Current discharge power: {discharge_power}%")  # noqa: T201

except growattServer.GrowattV1ApiError as e:
    print(f"API Error: {e} (Code: {e.error_code}, Message: {e.error_msg})")  # noqa: T201
except growattServer.GrowattParameterError as e:
    print(f"Parameter Error: {e}")  # noqa: T201
except requests.exceptions.RequestException as e:
    print(f"Network Error: {e}")  # noqa: T201
except Exception as e:  # noqa: BLE001
    print(f"Unexpected error: {e}")  # noqa: T201
