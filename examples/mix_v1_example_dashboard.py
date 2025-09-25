
from . import growattServer
import json
import requests
import os


def safe_float(val, default=0.0):
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
            val = val.replace(',', '').strip()
            return float(val)
        # If it's a type that can be cast to float (e.g., numpy.float64)
        return float(val)
    except (TypeError, ValueError, KeyError, AttributeError):
        return default


"""
Example script fetching key power and today+total energy metrics from a Growatt MID-30KTL3-XH (TLX) + APX battery hybrid system
using the V1 API with token-based authentication.
"""


# Get the API token from user input or environment variable
api_token = os.environ.get("GROWATT_API_TOKEN") or input("Enter your Growatt API token: ")


# test token from official API docs https://www.showdoc.com.cn/262556420217021/1494053950115877
# api_token = "6eb6f069523055a339d71e5b1f6c88cc"  # gitleaks:allow


try:
    # Initialize the API with token
    api = growattServer.OpenApiV1(token=api_token)

    # Plant info
    plants = api.plant_list()
    print(f"Plants: Found {plants['count']} plants")
    plant_id = plants['plants'][0]['plant_id']

    # Devices
    devices = api.device_list(plant_id)

    # Iterate over all devices
    energy_data = None
    for device in devices['devices']:
        print(device)
        if device['device_type'] == growattServer.DeviceType.MIX_SPH:
            inverter_sn = device['device_sn']
            device_type = device['device_type']
            print(f"Processing {device_type.name} inverter: {inverter_sn}")
            # Get energy data
            energy_data = api.device_energy(device_sn=inverter_sn, device_type=device_type)
            with open('energy_data.json', 'w') as f:
                json.dump(energy_data, f, indent=4, sort_keys=True)

    if energy_data is None:
        raise Exception("No MIX_SPH device found to get energy data from.")


    solar_production = f'{safe_float(energy_data.get('epvtoday')):.1f}/{safe_float(energy_data.get("epvTotal")):.1f}'
    solar_production_pv1 = f'{safe_float(energy_data.get("epv1Today")):.1f}/{safe_float(energy_data.get("epv1Total")):.1f}'
    solar_production_pv2 = f'{safe_float(energy_data.get("epv2Today")):.1f}/{safe_float(energy_data.get("epv2Total")):.1f}'
    energy_output = f'{safe_float(energy_data.get("eacToday")):.1f}/{safe_float(energy_data.get("eacTotal")):.1f}'
    system_production = f'{safe_float(energy_data.get("esystemtoday")):.1f}/{safe_float(energy_data.get("esystemtotal")):.1f}'
    battery_charged = f'{safe_float(energy_data.get("echarge1Today")):.1f}/{safe_float(energy_data.get("echarge1Total")):.1f}'
    battery_grid_charge = f'{safe_float(energy_data.get("acChargeEnergyToday")):.1f}/{safe_float(energy_data.get("acChargeEnergyTotal")):.1f}'
    battery_discharged = f'{safe_float(energy_data.get("edischarge1Today")):.1f}/{safe_float(energy_data.get("edischarge1Total")):.1f}'
    exported_to_grid = f'{safe_float(energy_data.get("etoGridToday")):.1f}/{safe_float(energy_data.get("etogridTotal")):.1f}'
    imported_from_grid = f'{safe_float(energy_data.get("etoUserToday")):.1f}/{safe_float(energy_data.get("etoUserTotal")):.1f}'
    load_consumption = f'{safe_float(energy_data.get("elocalLoadToday")):.1f}/{safe_float(energy_data.get("elocalLoadTotal")):.1f}'
    self_consumption = f'{safe_float(energy_data.get("elocalLoadToday")):.1f}/{safe_float(energy_data.get("elocalLoadTotal")):.1f}'

    # Output the dashboard
    print("\nGeneration overview             Today/Total(kWh)")
    print(f'Solar production          {solar_production:>22}')
    print(f' Solar production, PV1    {solar_production_pv1:>22}')
    print(f' Solar production, PV2    {solar_production_pv2:>22}')
    print(f'Energy Output             {energy_output:>22}')
    print(f'System production         {system_production:>22}')
    print(f'Self consumption          {self_consumption:>22}')
    print(f'Load consumption          {load_consumption:>22}')
    print(f'Battery Charged           {battery_charged:>22}')
    print(f' Charged from grid        {battery_grid_charge:>22}')
    print(f'Battery Discharged        {battery_discharged:>22}')
    print(f'Import from grid          {imported_from_grid:>22}')
    print(f'Export to grid            {exported_to_grid:>22}')

    print("\nPower overview                          (Watts)")
    print(f'AC Power                 {safe_float(energy_data.get("pac")):>22.1f}')
    print(f'Self power               {safe_float(energy_data.get("pself")):>22.1f}')
    print(f'Export power             {safe_float(energy_data.get("pacToGridTotal")):>22.1f}')
    print(f'Import power             {safe_float(energy_data.get("pacToUserTotal")):>22.1f}')
    print(f'Local load power         {safe_float(energy_data.get("pacToLocalLoad")):>22.1f}')
    print(f'PV power                 {safe_float(energy_data.get("ppv")):>22.1f}')
    print(f'PV #1 power              {safe_float(energy_data.get("ppv1")):>22.1f}')
    print(f'PV #2 power              {safe_float(energy_data.get("ppv2")):>22.1f}')
    print(f'Battery charge power     {safe_float(energy_data.get("bdc1ChargePower")):>22.1f}')
    print(f'Battery discharge power  {safe_float(energy_data.get("bdc1DischargePower")):>22.1f}')
    print(f'Battery SOC              {int(safe_float(energy_data.get("bmsSOC"))):>21}%')

except growattServer.GrowattV1ApiError as e:
    print(f"API Error: {e} (Code: {e.error_code}, Message: {e.error_msg})")
except growattServer.GrowattParameterError as e:
    print(f"Parameter Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Network Error: {e}")
except Exception as e:
    import traceback
    print(f"Unexpected error: {e}")
    traceback.print_exc()
