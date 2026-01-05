#!/usr/bin/env python3
"""
Example script for writing time segments to a Growatt SPH/MIX inverter.

This example demonstrates how to set AC charge time periods on SPH/MIX devices
using the write_time_segment method with proper parameter objects.
"""

import os

import growattServer


def main() -> None:
    """Main example function."""
    # Get the API token from user input or environment variable
    api_token = os.environ.get("GROWATT_API_TOKEN") or input("Enter your Growatt API token: ")

    # Test token from official API docs (for testing only)
    # api_token = "6eb6f069523055a339d71e5b1f6c88cc"  # gitleaks:allow

    try:
        # Initialize the API with token
        api = growattServer.OpenApiV1(token=api_token)

        # Get plant information
        plants = api.plant_list()
        print(f"Found {plants['count']} plants")  # noqa: T201

        if plants["count"] == 0:
            print("No plants found!")  # noqa: T201
            return

        plant_id = plants["plants"][0]["plant_id"]
        print(f"Using plant ID: {plant_id}")  # noqa: T201

        # Get devices
        devices = api.device_list(plant_id)
        print(f"Found {devices['count']} devices")  # noqa: T201

        # Find SPH_MIX device
        sph_mix_device = None
        for device in devices["devices"]:
            if device["device_type"] == growattServer.DeviceType.SPH_MIX:
                sph_mix_device = device
                break

        if not sph_mix_device:
            print("No SPH/MIX device found!")  # noqa: T201
            return

        device_sn = sph_mix_device["device_sn"]
        print(f"Found SPH/MIX device: {device_sn}")  # noqa: T201

        # Example 1: Set AC charge time period with high power charging
        print("\n=== Setting AC Charge Time Period ===")  # noqa: T201

        charge_params = api.MixAcChargeTimeParams(
            charge_power=80,           # 80% charging power
            charge_stop_soc=95,        # Stop charging at 95% SOC
            mains_enabled=True,        # Enable mains charging
            start_hour=23,             # Start at 23:00 (11 PM)
            start_minute=0,
            end_hour=6,                # End at 06:00 (6 AM)
            end_minute=0,
            enabled=True               # Enable this time period
        )

        result = api.write_time_segment(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.SPH_MIX,
            command="mix_ac_charge_time_period",
            params=charge_params
        )

        print(f"AC charge time period set successfully: {result}")  # noqa: T201

        # Example 2: Alternative approach using write_parameter method
        print("\n=== Alternative: Using write_parameter method ===")  # noqa: T201

        # Set a different charge time period (off-peak hours)
        charge_params2 = api.MixAcChargeTimeParams(
            charge_power=100,          # 100% charging power
            charge_stop_soc=100,       # Charge to full
            mains_enabled=True,        # Enable mains charging
            start_hour=1,              # Start at 01:00 (1 AM)
            start_minute=30,
            end_hour=5,                # End at 05:00 (5 AM)
            end_minute=30,
            enabled=True
        )

        result2 = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.SPH_MIX,
            command="mix_ac_charge_time_period",
            params=charge_params2
        )

        print(f"Alternative charge time period set: {result2}")  # noqa: T201

        # Example 3: Disable charging during a specific period
        print("\n=== Disabling Charge Time Period ===")  # noqa: T201

        disable_charge_params = api.MixAcChargeTimeParams(
            charge_power=0,            # No charging power
            charge_stop_soc=0,         # No stop SOC
            mains_enabled=False,       # Disable mains charging
            start_hour=12,             # Noon
            start_minute=0,
            end_hour=18,               # 6 PM
            end_minute=0,
            enabled=False              # Disable this time period
        )

        result3 = api.write_parameter(
            device_sn=device_sn,
            device_type=growattServer.DeviceType.SPH_MIX,
            command="mix_ac_charge_time_period",
            params=disable_charge_params
        )

        print(f"Charge time period disabled: {result3}")  # noqa: T201

        # Example 4: Read current settings to verify changes
        print("\n=== Reading Current Settings ===")  # noqa: T201

        settings = api.device_settings(device_sn, growattServer.DeviceType.SPH_MIX)

        # Display relevant charge time settings
        print("Current charge time settings:")  # noqa: T201
        for i in range(1, 4):  # Typically 3 time periods
            start_key = f"forcedChargeTimeStart{i}"
            stop_key = f"forcedChargeTimeStop{i}"
            enabled_key = f"forcedChargeStopSwitch{i}"

            if start_key in settings:
                print(f"  Period {i}:")  # noqa: T201
                print(f"    Start: {settings.get(start_key, 'N/A')}")  # noqa: T201
                print(f"    Stop: {settings.get(stop_key, 'N/A')}")  # noqa: T201
                print(f"    Enabled: {settings.get(enabled_key, 'N/A')}")  # noqa: T201

    except growattServer.GrowattV1ApiError as e:
        print(f"API Error: {e} (Code: {e.error_code}, Message: {e.error_msg})")  # noqa: T201
    except growattServer.GrowattParameterError as e:
        print(f"Parameter Error: {e}")  # noqa: T201
    except Exception as e:  # noqa: BLE001
        print(f"Unexpected error: {e}")  # noqa: T201
        import traceback
        traceback.print_exc()


def demonstrate_other_parameters() -> None:
    """Demonstrate other parameter types for SPH_MIX devices."""
    print("\n=== Other Parameter Examples ===")  # noqa: T201

    # Note: These are just examples of parameter creation
    # You would use them with api.write_parameter() as shown above

    # Backflow setting
    backflow_params = growattServer.OpenApiV1.BackflowSettingParams(
        backflow_enabled=True,
        anti_reverse_power_percentage=50  # 50% anti-reverse flow power
    )
    print(f"Backflow params: {backflow_params}")  # noqa: T201

    # PV on/off control
    pv_params = growattServer.OpenApiV1.PvOnOffParams(
        pv_enabled=True  # Turn PV on
    )
    print(f"PV control params: {pv_params}")  # noqa: T201

    # Grid voltage limits
    voltage_params = growattServer.OpenApiV1.GridVoltageParams(
        voltage_high=270,  # Upper limit
        voltage_low=180    # Lower limit
    )
    print(f"Voltage params: {voltage_params}")  # noqa: T201

    # Off-grid settings
    offgrid_params = growattServer.OpenApiV1.OffGridParams(
        off_grid_enabled=True,
        frequency=0,  # 50Hz
        voltage=0     # 230V
    )
    print(f"Off-grid params: {offgrid_params}")  # noqa: T201


if __name__ == "__main__":
    main()
    demonstrate_other_parameters()
