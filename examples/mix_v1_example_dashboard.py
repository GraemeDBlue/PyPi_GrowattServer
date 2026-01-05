"""Example dashboard for MIX inverters using V1 API."""

import datetime
import os

import requests

from . import growattServer


def safe_float(val: str | float, default: float = 0.0) -> float:
    """Safely convert a value to float with a default fallback."""
    try:
        # If already a float, return as is
        if isinstance(val, float):
            return val
        # If it's an int, convert to float
        if isinstance(val, int):
            return float(val)
        # If it's a string, try to parse
        if isinstance(val, str):
            # Remove any commas, spaces, etc.
            val = val.replace(",", "").strip()
            return float(val)
        # If it's a type that can be cast to float (e.g., numpy.float64)
        return float(val)
    except (TypeError, ValueError, KeyError, AttributeError):
        return default


"""
Example script controlling a MIX/SPH Growatt system.  # noqa: E501

For SPH3~6k TL BL UP + battery systems using the public growatt API.
You can obtain an API token from the Growatt API documentation or developer portal.
"""

# Get the API token from user input or environment variable
api_token = os.environ.get("GROWATT_API_TOKEN") or input(
    "Enter your Growatt API token: "
)

# test token from official API docs https://www.showdoc.com.cn/262556420217021/1494053950115877
# api_token = "6eb6f069523055a339d71e5b1f6c88cc"  # gitleaks:allow  # noqa: ERA001

try:
    # Initialize the API with token
    api = growattServer.OpenApiV1(token=api_token)

    # Plant info
    plants = api.plant_list()
    print(f"Plants: Found {plants['count']} plants")  # noqa: T201
    plant_id = plants["plants"][0]["plant_id"]
    today = datetime.datetime.now(tz=datetime.UTC).date()
    devices = api.get_devices(plant_id)

    energy_data = None
    for device in devices:
        # Works automatically for MIN, MIX, or any future device type!
        device_type = device.device_type
        device_sn = device.device_sn
        print(f"Device: {device_type} SN: {device_sn}")  # noqa: T201
        energy_data = device.energy()
        print(f"Energy: {energy_data}")  # noqa: T201

    if energy_data is None:
        msg = "No SPH_MIX device found to get energy data from."
        raise RuntimeError(msg)  # noqa: TRY301

    solar_production = f"{safe_float(energy_data.get('epvtoday')):.1f}/{safe_float(energy_data.get('epvTotal')):.1f}"  # noqa: E501
    solar_production_pv1 = f"{safe_float(energy_data.get('epv1Today')):.1f}/{safe_float(energy_data.get('epv1Total')):.1f}"  # noqa: E501
    solar_production_pv2 = f"{safe_float(energy_data.get('epv2Today')):.1f}/{safe_float(energy_data.get('epv2Total')):.1f}"  # noqa: E501
    energy_output = f"{safe_float(energy_data.get('eacToday')):.1f}/{safe_float(energy_data.get('eacTotal')):.1f}"  # noqa: E501
    system_production = f"{safe_float(energy_data.get('esystemtoday')):.1f}/{safe_float(energy_data.get('esystemtotal')):.1f}"  # noqa: E501
    battery_charged = f"{safe_float(energy_data.get('echarge1Today')):.1f}/{safe_float(energy_data.get('echarge1Total')):.1f}"  # noqa: E501
    battery_grid_charge = f"{safe_float(energy_data.get('acChargeEnergyToday')):.1f}/{safe_float(energy_data.get('acChargeEnergyTotal')):.1f}"  # noqa: E501
    battery_discharged = f"{safe_float(energy_data.get('edischarge1Today')):.1f}/{safe_float(energy_data.get('edischarge1Total')):.1f}"  # noqa: E501
    exported_to_grid = f"{safe_float(energy_data.get('etoGridToday')):.1f}/{safe_float(energy_data.get('etogridTotal')):.1f}"  # noqa: E501
    imported_from_grid = f"{safe_float(energy_data.get('etoUserToday')):.1f}/{safe_float(energy_data.get('etoUserTotal')):.1f}"  # noqa: E501
    load_consumption = f"{safe_float(energy_data.get('elocalLoadToday')):.1f}/{safe_float(energy_data.get('elocalLoadTotal')):.1f}"  # noqa: E501
    self_consumption = f"{safe_float(energy_data.get('eselfToday')):.1f}/{safe_float(energy_data.get('eselfTotal')):.1f}"  # noqa: E501

    # Output the dashboard
    print("\nGeneration overview             Today/Total(kWh)")  # noqa: T201
    print(f"Solar production          {solar_production:>22}")  # noqa: T201
    print(f" Solar production, PV1    {solar_production_pv1:>22}")  # noqa: T201
    print(f" Solar production, PV2    {solar_production_pv2:>22}")  # noqa: T201
    print(f"Energy Output             {energy_output:>22}")  # noqa: T201
    print(f"System production         {system_production:>22}")  # noqa: T201
    print(f"Self consumption          {self_consumption:>22}")  # noqa: T201
    print(f"Load consumption          {load_consumption:>22}")  # noqa: T201
    print(f"Battery Charged           {battery_charged:>22}")  # noqa: T201
    print(f" Charged from grid        {battery_grid_charge:>22}")  # noqa: T201
    print(f"Battery Discharged        {battery_discharged:>22}")  # noqa: T201
    print(f"Import from grid          {imported_from_grid:>22}")  # noqa: T201
    print(f"Export to grid            {exported_to_grid:>22}")  # noqa: T201

    print("\nPower overview                          (Watts)")  # noqa: T201
    print(f"AC Power                 {safe_float(energy_data.get('pac')):>22.1f}")  # noqa: T201
    print(f"Self power               {safe_float(energy_data.get('pself')):>22.1f}")  # noqa: T201
    print(f"PV power                 {safe_float(energy_data.get('ppv')):>22.1f}")  # noqa: T201
    print(f"PV #1 power              {safe_float(energy_data.get('ppv1')):>22.1f}")  # noqa: T201
    print(f"PV #2 power              {safe_float(energy_data.get('ppv2')):>22.1f}")  # noqa: T201
    print(f"Battery SOC              {int(safe_float(energy_data.get('bmsSOC'))):>21}%")  # noqa: T201

except growattServer.GrowattV1ApiError as e:
    print(f"API Error: {e} (Code: {e.error_code}, Message: {e.error_msg})")  # noqa: T201
except growattServer.GrowattParameterError as e:
    print(f"Parameter Error: {e}")  # noqa: T201
except requests.exceptions.RequestException as e:
    print(f"Network Error: {e}")  # noqa: T201
except Exception as e:  # noqa: BLE001
    import traceback

    print(f"Unexpected error: {e}")  # noqa: T201
    traceback.print_exc()
