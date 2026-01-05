#!/usr/bin/env python3
"""
Example script demonstrating generic parameter writing for Growatt devices.

This script shows how to use the write_parameter() method to set various
parameters on both SPH_MIX and MIN_TLX device types using the V1 API.
"""

import os
import traceback
from datetime import time

import requests

from . import growattServer


def demonstrate_sph_mix_parameters(
    api: growattServer.GrowattApi, device_sn: str
) -> None:
    """Demonstrate parameter writing for SPH_MIX devices."""
    print(f"\n=== SPH_MIX Device Parameters for {device_sn} ===")  # noqa: T201

    try:
        # 1. AC Charge Time Period
        print("Setting AC charge time period...")  # noqa: T201
        charge_params = api.MixAcChargeTimeParams(
            charge_power=80,  # 80% charging power
            charge_stop_soc=95,  # Stop at 95% SOC
            mains_enabled=True,  # Enable mains charging
            start_hour=14,  # Start at 14:00
            start_minute=0,
            end_hour=16,  # End at 16:00
            end_minute=0,
            enabled=True,
        )
        result = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.SPH_MIX,
            command="mix_ac_charge_time_period",
            params=charge_params,
        )
        print(f"AC charge time period result: {result}")  # noqa: T201

    except Exception as e:  # noqa: BLE001
        print(f"Error with SPH_MIX parameters: {e}")  # noqa: T201


def demonstrate_min_tlx_parameters(
    api: growattServer.GrowattApi, device_sn: str
) -> None:
    """Demonstrate parameter writing for MIN_TLX devices."""
    print(f"\n=== MIN_TLX Device Parameters for {device_sn} ===")  # noqa: T201

    try:
        # 1. Time Segments (TOU settings)
        print("Setting time segment 1...")  # noqa: T201
        time_params = api.TimeSegmentParams(
            segment_id=1,
            batt_mode=1,  # Battery First
            start_time=time(8, 0),  # 08:00
            end_time=time(16, 0),  # 16:00
            enabled=True,
        )
        result = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.MIN_TLX,
            command="time_segment1",
            params=time_params,
        )
        print(f"Time segment 1 result: {result}")  # noqa: T201

        # 2. Backflow Setting (different params for MIN_TLX)
        print("Setting backflow prevention...")  # noqa: T201
        backflow_params = api.BackflowSettingParams(
            backflow_enabled=True,
            backflow_mode=1,  # Enable meter mode for MIN_TLX
        )
        result = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.MIN_TLX,
            command="backflow_setting",
            params=backflow_params,
        )
        print(f"Backflow setting result: {result}")  # noqa: T201

        # 3. Charge/Discharge Parameters
        print("Setting charge/discharge parameters...")  # noqa: T201
        charge_discharge_params = api.ChargeDischargeParams(
            charge_power=90,  # 90% charge power
            charge_stop_soc=100,  # Charge to 100%
            discharge_power=80,  # 80% discharge power
            discharge_stop_soc=10,  # Stop at 10%
            ac_charge_enabled=True,  # Enable AC charging
        )

        # Set charge power
        result = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.MIN_TLX,
            command="charge_power",
            params=charge_discharge_params,
        )
        print(f"Charge power result: {result}")  # noqa: T201

        # Set discharge power
        result = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.MIN_TLX,
            command="discharge_power",
            params=charge_discharge_params,
        )
        print(f"Discharge power result: {result}")  # noqa: T201

        # 4. PV On/Off Control
        print("Turning PV on...")  # noqa: T201
        pv_params = api.PvOnOffParams(pv_enabled=True)
        result = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.MIN_TLX,
            command="tlx_on_off",
            params=pv_params,
        )
        print(f"PV on/off result: {result}")  # noqa: T201

        # 5. Power Factor Settings
        print("Setting power factor...")  # noqa: T201
        power_params = api.PowerParams(
            active_power=100,  # 100% active power
            reactive_power=0,  # 0% reactive power
            power_factor=1.0,  # Unity power factor
        )
        result = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.MIN_TLX,
            command="pv_power_factor",
            params=power_params,
        )
        print(f"Power factor result: {result}")  # noqa: T201

    except Exception as e:  # noqa: BLE001
        print(f"Error with MIN_TLX parameters: {e}")  # noqa: T201


def main() -> None:  # noqa: PLR0912
    """Run the main demonstration for V1 API parameter writing."""
    # Get the API token from user input or environment variable
    api_token = os.environ.get("GROWATT_API_TOKEN") or input(
        "Enter your Growatt API token: "
    )

    # Test token from official API docs (for testing only)
    # api_token = "6eb6f069523055a339d71e5b1f6c88cc"  # gitleaks:allow  # noqa: ERA001

    try:
        # Initialize the API with token
        api = growattServer.OpenApiV1(token=api_token)

        # Plant info
        plants = api.plant_list()
        print(f"Plants: Found {plants['count']} plants")  # noqa: T201

        if plants["count"] == 0:
            print("No plants found!")  # noqa: T201
            return

        plant_id = plants["plants"][0]["plant_id"]
        print(f"Using plant ID: {plant_id}")  # noqa: T201

        # Get devices
        devices = api.get_devices(plant_id)
        print(f"Found {len(devices)} devices")  # noqa: T201

        # Demonstrate parameters for each device type
        for device in devices:
            device_type = device.device_type
            device_sn = device.device_sn

            print(f"\n{'=' * 60}")  # noqa: T201
            print(f"Processing Device: {device_type.name} - SN: {device_sn}")  # noqa: T201
            print(f"{'=' * 60}")  # noqa: T201

            if device_type == growattServer.DeviceType.SPH_MIX:
                demonstrate_sph_mix_parameters(api, device_sn)
            elif device_type == growattServer.DeviceType.MIN_TLX:
                demonstrate_min_tlx_parameters(api, device_sn)
            else:
                print(f"Device type {device_type.name} not supported in this example")  # noqa: T201

            # Read current settings to verify changes
            print(f"\n--- Reading current settings for {device_sn} ---")  # noqa: T201
            try:
                settings = device.settings()

                # Show some relevant settings based on device type
                if device_type == growattServer.DeviceType.SPH_MIX:
                    for i in range(1, 4):
                        start_key = f"forcedChargeTimeStart{i}"
                        if start_key in settings:
                            pass

                elif device_type == growattServer.DeviceType.MIN_TLX:
                    for i in range(1, 4):
                        start_key = f"forcedTimeStart{i}"
                        if start_key in settings:
                            pass

            except Exception as e:  # noqa: BLE001
                print(f"Error reading settings: {e}")  # noqa: T201

        print(f"\n{'=' * 60}")  # noqa: T201
        print("Parameter writing demonstration completed!")  # noqa: T201
        print(f"{'=' * 60}")  # noqa: T201

    except growattServer.GrowattV1ApiError as e:
        print(f"API Error: {e} (Code: {e.error_code}, Message: {e.error_msg})")  # noqa: T201
    except growattServer.GrowattParameterError as e:
        print(f"Parameter Error: {e}")  # noqa: T201
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")  # noqa: T201
    except Exception as e:  # noqa: BLE001
        print(f"Unexpected error: {e}")  # noqa: T201
        traceback.print_exc()


if __name__ == "__main__":
    main()
