from . import growattServer
import datetime
import json
import requests
import os

"""
# Example script controlling a MIX/SPH Growatt (SPH3~6k TL BL UP + battery) system using the public growatt API 
# You can obtain an API token from the Growatt API documentation or developer portal.
"""

# Get the API token from user input or environment variable
api_token = os.environ.get("GROWATT_API_TOKEN") or input("Enter your Growatt API token: ")

# test token from official API docs https://www.showdoc.com.cn/262556420217021/1494053950115877
# api_token = "6eb6f069523055a339d71e5b1f6c88cc"  # gitleaks:allow

try:
    # Initialize the API with token instead of using login
    api = growattServer.OpenApiV1(token=api_token)

    # Plant info
    plants = api.plant_list()
    print(f"Plants: Found {plants['count']} plants")
    plant_id = plants['plants'][0]['plant_id']
    today = datetime.date.today()
    devices = api.get_devices(plant_id)

    for device in devices:
        # Works automatically for MIN, MIX, or any future device type!
        device_type = device.device_type
        device_sn = device.device_sn
        print(f"Device: {device_type} SN: {device_sn}")
        details = device.details()
        energy = device.energy()
        settings = device.settings()
        history = device.energy_history(start_date=today)

        print(f"Details: {details}")
        print(f"Energy: {energy}")
        print(f"Settings: {settings}")
        print(f"History: {history}")

except growattServer.GrowattV1ApiError as e:
    print(f"API Error: {e} (Code: {e.error_code}, Message: {e.error_msg})")
except growattServer.GrowattParameterError as e:
    print(f"Parameter Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Network Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
