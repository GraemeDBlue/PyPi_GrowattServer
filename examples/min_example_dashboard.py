"""
Example dashboard script for MIN/TLX Growatt inverters.

This script demonstrates controlling a MID/TLX Growatt
(MID-30KTL3-XH + APX battery) system using the public Growatt API
and displays energy data in a dashboard format.
You can obtain an API token from the Growatt API documentation or
developer portal.
"""

import datetime
from typing import Any

import requests

from . import growattServer


def safe_float(val: Any, default: float = 0.0) -> float:
    """Convert a value to float safely, returning default on failure.

    Args:
        val: The value to convert to float.
        default: The default value to return if conversion fails.

    Returns:
        The value as a float, or the default if conversion fails.

    """
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


# Test token from official API docs
# https://www.showdoc.com.cn/262556420217021/1494053950115877
api_token = "6eb6f069523055a339d71e5b1f6c88cc"  # noqa: S105

try:
    # Initialize the API with token
    api = growattServer.OpenApiV1(token=api_token)

    # Plant info
    plants = api.plant_list()
    print(f"Plants: Found {plants['count']} plants")  # noqa: T201
    plant_id = plants["plants"][0]["plant_id"]
    today = datetime.date.today()
    devices = api.get_devices(plant_id)

    energy_data = None
    for device in devices:
        # Works automatically for MIN, MIX, or any future device type!
        energy_data = device.energy()
        print(f"Energy: {energy_data}")  # noqa: T201
        
    if energy_data is None:
        msg = "No MIN_TLX device found to get energy data from."
        raise RuntimeError(msg)

    # energy data does not contain epvToday for some reason, so we need to calculate it
    # Dynamically calculate epvToday by summing all epvXToday fields
    epv_today = sum(
        safe_float(energy_data.get(f"epv{i}Today"), 0.0)
        for i in range(1, 4)  # Assuming a maximum of 4 devices
        if f"epv{i}Today" in energy_data
    )

    solar_production = f'{safe_float(epv_today):.1f}/{safe_float(energy_data.get("epvTotal")):.1f}'
    solar_production_pv1 = f'{safe_float(energy_data.get("epv1Today")):.1f}/{safe_float(energy_data.get("epv1Total")):.1f}'
    solar_production_pv2 = f'{safe_float(energy_data.get("epv2Today")):.1f}/{safe_float(energy_data.get("epv2Total")):.1f}'
    energy_output = f'{float(energy_data["eacToday"]):.1f}/{float(energy_data["eacTotal"]):.1f}'
    system_production = f'{float(energy_data["esystemToday"]):.1f}/{float(energy_data["esystemTotal"]):.1f}'
    battery_charged = f'{float(energy_data["echargeToday"]):.1f}/{float(energy_data["echargeTotal"]):.1f}'
    battery_grid_charge = f'{float(energy_data["eacChargeToday"]):.1f}/{float(energy_data["eacChargeTotal"]):.1f}'
    battery_discharged = f'{float(energy_data["edischargeToday"]):.1f}/{float(energy_data["edischargeTotal"]):.1f}'
    exported_to_grid = f'{float(energy_data["etoGridToday"]):.1f}/{float(energy_data["etoGridTotal"]):.1f}'
    imported_from_grid = f'{float(energy_data["etoUserToday"]):.1f}/{float(energy_data["etoUserTotal"]):.1f}'
    load_consumption = f'{float(energy_data["elocalLoadToday"]):.1f}/{float(energy_data["elocalLoadTotal"]):.1f}'
    self_consumption = f'{float(energy_data["eselfToday"]):.1f}/{float(energy_data["eselfTotal"]):.1f}'
    battery_charged = f'{float(energy_data["echargeToday"]):.1f}/{float(energy_data["echargeTotal"]):.1f}'

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
    print(f"AC Power                  {float(energy_data['pac']):>22.1f}")  # noqa: T201
    print(f"Self power                {float(energy_data['pself']):>22.1f}")  # noqa: T201
    print(
        f"Export power                {float(energy_data['pacToGridTotal']):>22.1f}")  # noqa: T201, E501
    print(
        f"Import power                {float(energy_data['pacToUserTotal']):>22.1f}")  # noqa: T201, E501
    print(
        f"Local load power            {float(energy_data['pacToLocalLoad']):>22.1f}")  # noqa: T201, E501
    print(f"PV power                  {float(energy_data['ppv']):>22.1f}")  # noqa: T201
    print(f"PV #1 power               {float(energy_data['ppv1']):>22.1f}")  # noqa: T201
    print(f"PV #2 power               {float(energy_data['ppv2']):>22.1f}")  # noqa: T201
    print(
        f"Battery charge power        {float(energy_data['bdc1ChargePower']):>22.1f}")  # noqa: T201, E501
    print(
        f"Battery discharge power     {float(energy_data['bdc1DischargePower']):>22.1f}")  # noqa: T201, E501
    print(f"Battery SOC               {int(energy_data['bdc1Soc']):>21}%")  # noqa: T201

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
