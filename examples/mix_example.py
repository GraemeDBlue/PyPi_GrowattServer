#!/usr/bin/env python3
"""
Example script for MIX/SPH Growatt systems (Hybrid).

This is a script that logs into a user's account and prints out useful
data for a "Mix" system (Hybrid). The first half of the logic is
applicable to all types of system. There is a clear point (marked in the
script) where we specifically make calls to the "mix" WebAPI calls, at
this point other types of systems will no longer work.

This has been tested against a hybrid inverter system.

Throughout the script there are points where 'pp.pprint' has been
commented out. If you wish to see all the data that is returned from
those specific library calls, just uncomment them and they will appear
as part of the output.

NOTE - For some reason (not sure if this is just specific to some
systems or not) the "export to grid" daily total and overall total
values don't seem to be populating. As such they are untested. This has
been causing problems on WebUI and mobile app too, it is not a bug in
this library, the output from this script has been updated to reflect
its inaccuracy.
"""

import getpass
import json
import pprint
from pathlib import Path

from . import growattServer

pp = pprint.PrettyPrinter(indent=4)


def indent_print(to_output: str, indent: int) -> None:
    """
    Print output with leading spaces for indentation.

    Args:
        to_output: The string to print.
        indent: The number of spaces to indent.

    """
    indent_string = " " * indent
    print(indent_string + to_output)  # noqa: T201


# Prompt user for username
username = input("Enter username:")

# Prompt user to input password
user_pass = getpass.getpass("Enter password:")

api = growattServer.GrowattApi()
login_response = api.login(username, user_pass)

plant_list = api.plant_list(login_response["user"]["id"])

print("***Totals for all plants***")  # noqa: T201
pp.pprint(plant_list["totalData"])
print()  # noqa: T201

print("***List of plants***")  # noqa: T201
for plant in plant_list["data"]:
    indent_print(f"ID: {plant['plantId']}, Name: {plant['plantName']}", 2)
print()  # noqa: T201

for plant in plant_list["data"]:
    plant_id = plant["plantId"]
    plant_name = plant["plantName"]
    plant_info = api.plant_info(plant_id)
    print(f"***Info for Plant {plant_id} - {plant_name}***")  # noqa: T201
    # There are more values in plant_info, but these are some of the
    # useful/interesting ones
    indent_print(f"CO2 Reducion: {plant_info['Co2Reduction']}", 2)
    indent_print(f"Nominal Power (w): {plant_info['nominal_Power']}", 2)
    indent_print(f"Solar Energy Today (kw): {plant_info['todayEnergy']}", 2)
    indent_print(f"Solar Energy Total (kw): {plant_info['totalEnergy']}", 2)
    print()  # noqa: T201
    indent_print("Devices in plant:", 2)
    for device in plant_info["deviceList"]:
        device_sn = device["deviceSn"]
        device_type = device["deviceType"]
        indent_print(f"- Device - SN: {device_sn}, Type: {device_type}", 4)

    print()  # noqa: T201
    for device in plant_info["deviceList"]:
        device_sn = device["deviceSn"]
        device_type = device["deviceType"]
        indent_print(f"**Device - SN: {device_sn}, Type: {device_type}**", 2)
        # NOTE - This is the bit where we specifically only handle information on Mix devices  # noqa: E501
        # - this won't work for non-mix devices

        # These two API calls return lots of duplicated information,
        # but each also holds unique information as well
        mix_info = api.mix_info(device_sn, plant_id)
        pp.pprint(mix_info)

        print("Saving inverter data to old_inverter_data.json")  # noqa: T201
        with Path("old_inverter_data.json").open("w") as f:
            json.dump(mix_info, f, indent=4, sort_keys=True)

        mix_totals = api.mix_totals(device_sn, plant_id)
        print("Saving energy data to old_energy_data.json")  # noqa: T201
        with Path("old_energy_data.json").open("w") as f:
            json.dump(mix_totals, f, indent=4, sort_keys=True)

        # pp.pprint(mix_totals)  # noqa: ERA001
        indent_print("*TOTAL VALUES*", 4)
        indent_print("==Today Totals==", 4)
        indent_print(f"Battery Charge (kwh): {mix_info['eBatChargeToday']}", 6)
        indent_print(f"Battery Discharge (kwh): {mix_info['eBatDisChargeToday']}", 6)
        indent_print(f"Solar Generation (kwh): {mix_info['epvToday']}", 6)
        indent_print(f"Local Load (kwh): {mix_totals['elocalLoadToday']}", 6)
        indent_print(f"Export to Grid (kwh): {mix_totals['etoGridToday']}", 6)
        indent_print("==Overall Totals==", 4)
        indent_print(f"Battery Charge: {mix_info['eBatChargeTotal']}", 6)
        indent_print(f"Battery Discharge (kwh): {mix_info['eBatDisChargeTotal']}", 6)
        indent_print(f"Solar Generation (kwh): {mix_info['epvTotal']}", 6)
        indent_print(f"Local Load (kwh): {mix_totals['elocalLoadTotal']}", 6)
        indent_print(f"Export to Grid (kwh): {mix_totals['etogridTotal']}", 6)
        print()  # noqa: T201

        mix_detail = api.mix_detail(device_sn, plant_id)

        print("Saving energy data to old_detail_data.json")  # noqa: T201
        with Path("old_detail_data.json").open("w") as f:
            json.dump(mix_detail, f, indent=4, sort_keys=True)
        # pp.pprint(mix_detail)  # noqa: ERA001

        # Some of the 'totals' values that are returned by this function do not align  # noqa: E501
        # to what we would expect, however the graph data always seems to be accurate.
        # Therefore, here we take a moment to calculate the same values provided  # noqa: E501
        # elsewhere but based on the graph data instead
        # The particular stats that we question are 'load consumption' (elocalLoad)  # noqa: E501
        # and 'import from grid' (etouser) which seem to be calculated from one-another
        # It would appear that 'etouser' is calculated on the backend incorrectly  # noqa: E501
        # for systems that use AC battery charged (e.g. during cheap nighttime rates)
        pac_to_grid_today = 0.0
        pac_to_user_today = 0.0
        pdischarge_today = 0.0
        ppv_today = 0.0
        sys_out_today = 0.0

        chart_data = mix_detail["chartData"]
        for data_points in chart_data.values():
            # For each time entry convert it's wattage into kWh, this assumes  # noqa: E501
            # that the wattage value is the same for the whole 5 minute window  # noqa: E501
            # (it's the only assumption we can make)
            # We Multiply the wattage by 5/60 (the number of minutes of the time  # noqa: E501
            # window divided by the number of minutes in an hour) to give us the  # noqa: E501
            # equivalent kWh reading for that 5 minute window
            pac_to_grid_today += float(data_points["pacToGrid"]) * (5 / 60)
            pac_to_user_today += float(data_points["pacToUser"]) * (5 / 60)
            pdischarge_today += float(data_points["pdischarge"]) * (5 / 60)
            ppv_today += float(data_points["ppv"]) * (5 / 60)
            sys_out_today += float(data_points["sysOut"]) * (5 / 60)

        mix_detail["calculatedPacToGridTodayKwh"] = round(pac_to_grid_today, 2)
        mix_detail["calculatedPacToUserTodayKwh"] = round(pac_to_user_today, 2)
        mix_detail["calculatedPdischargeTodayKwh"] = round(pdischarge_today, 2)
        mix_detail["calculatedPpvTodayKwh"] = round(ppv_today, 2)
        mix_detail["calculatedSysOutTodayKwh"] = round(sys_out_today, 2)

        # Option to print mix_detail again now we've made the additions
        # pp.pprint(mix_detail)  # noqa: ERA001

        dashboard_data = api.dashboard_data(plant_id)
        # pp.pprint(dashboard_data)  # noqa: ERA001

        indent_print("*TODAY TOTALS BREAKDOWN*", 4)
        indent_print(
            f"Self generation total (batteries & solar - from API) (kwh): {mix_detail['eCharge']}",  # noqa: E501
            6,
        )
        indent_print(f"Load consumed from solar (kwh): {mix_detail['eChargeToday']}", 6)
        indent_print(f"Load consumed from batteries (kwh): {mix_detail['echarge1']}", 6)
        indent_print(
            f"Self consumption total (batteries & solar - from API) (kwh): {mix_detail['eChargeToday1']}",  # noqa: E501
            6,
        )
        indent_print(f"Load consumed from grid (kwh): {mix_detail['etouser']}", 6)
        indent_print(
            f"Total imported from grid (Load + AC charging) (kwh): {dashboard_data['etouser'].replace('kWh', '')}",  # noqa: E501
            6,
        )
        calculated_consumption = (
            float(mix_detail["eChargeToday"])
            + float(mix_detail["echarge1"])
            + float(mix_detail["etouser"])
        )
        indent_print(
            f"Load consumption (calculated) (kwh): {round(calculated_consumption, 2)}",
            6,
        )
        indent_print(f"Load consumption (API) (kwh): {mix_detail['elocalLoad']}", 6)

        indent_print(f"Exported (kwh): {mix_detail['eAcCharge']}", 6)

        solar_to_battery = round(
            float(mix_info["epvToday"])
            - float(mix_detail["eAcCharge"])
            - float(mix_detail["eChargeToday"]),
            2,
        )
        indent_print(f"Solar battery charge (calculated) (kwh): {solar_to_battery}", 6)
        ac_to_battery = round(float(mix_info["eBatChargeToday"]) - solar_to_battery, 2)
        indent_print(f"AC battery charge (calculated) (kwh): {ac_to_battery}", 6)
        print()  # noqa: T201

        indent_print("*TODAY TOTALS COMPARISONS*", 4)

        indent_print("Export to Grid (kwh) - TRUSTED:", 6)
        indent_print(f"mix_totals['etoGridToday']: {mix_totals['etoGridToday']}", 8)
        indent_print(f"mix_detail['eAcCharge']: {mix_detail['eAcCharge']}", 8)
        indent_print(
            f"mix_detail['calculatedPacToGridTodayKwh']: {mix_detail['calculatedPacToGridTodayKwh']}",  # noqa: E501
            8,
        )
        print()  # noqa: T201

        indent_print("Imported from Grid (kwh) - TRUSTED:", 6)
        indent_print(
            f"dashboard_data['etouser']: {dashboard_data['etouser'].replace('kWh', '')}",  # noqa: E501
            8,
        )
        indent_print(
            f"mix_detail['calculatedPacToUserTodayKwh']: {mix_detail['calculatedPacToUserTodayKwh']}",  # noqa: E501
            8,
        )
        print()  # noqa: T201

        indent_print("Battery discharge (kwh) - TRUSTED:", 6)
        indent_print(
            f"mix_info['eBatDisChargeToday']: {mix_info['eBatDisChargeToday']}", 8
        )
        indent_print(
            f"mix_totals['edischarge1Today']: {mix_totals['edischarge1Today']}", 8
        )
        indent_print(f"mix_detail['echarge1']: {mix_detail['echarge1']}", 8)
        indent_print(
            f"mix_detail['calculatedPdischargeTodayKwh']: {mix_detail['calculatedPdischargeTodayKwh']}",  # noqa: E501
            8,
        )
        print()  # noqa: T201

        indent_print("Solar generation (kwh) - TRUSTED:", 6)
        indent_print(f"mix_info['epvToday']: {mix_info['epvToday']}", 8)
        indent_print(f"mix_totals['epvToday']: {mix_totals['epvToday']}", 8)
        indent_print(
            f"mix_detail['calculatedPpvTodayKwh']: {mix_detail['calculatedPpvTodayKwh']}",  # noqa: E501
            8,
        )
        print()  # noqa: T201

        indent_print("Load Consumption (kwh) - TRUSTED:", 6)
        indent_print(
            f"mix_totals['elocalLoadToday']: {mix_totals['elocalLoadToday']}", 8
        )
        indent_print(f"mix_detail['elocalLoad']: {mix_detail['elocalLoad']}", 8)
        indent_print(
            f"mix_detail['calculatedSysOutTodayKwh']: {mix_detail['calculatedSysOutTodayKwh']}",  # noqa: E501
            8,
        )
        print()  # noqa: T201

        # This call gets all of the instantaneous values from the system
        # e.g. current load, generation etc.
        mix_status = api.mix_system_status(device_sn, plant_id)
        # pp.pprint(mix_status)  # noqa: ERA001
        # NOTE - There are some other values available in mix_status,
        # however these are the most useful ones
        indent_print("*CURRENT VALUES*", 4)
        indent_print("==Batteries==", 4)
        indent_print(f"Charging Batteries at (kw): {mix_status['chargePower']}", 6)
        indent_print(f"Discharging Batteries at (kw): {mix_status['pdisCharge1']}", 6)
        indent_print(f"Batteries %: {mix_status['SOC']}", 6)

        indent_print("==PVs==", 4)
        indent_print(f"PV1 wattage: {mix_status['pPv1']}", 6)
        indent_print(f"PV2 wattage: {mix_status['pPv2']}", 6)
        calc_pv_total = (float(mix_status["pPv1"]) + float(mix_status["pPv2"])) / 1000
        indent_print(
            f"PV total wattage (calculated) - KW: {round(calc_pv_total, 2)}", 6
        )
        indent_print(f"PV total wattage (API) - KW: {mix_status['ppv']}", 6)

        indent_print("==Consumption==", 4)
        indent_print(f"Local load/consumption - KW: {mix_status['pLocalLoad']}", 6)

        indent_print("==Import/Export==", 4)
        indent_print(f"Importing from Grid - KW: {mix_status['pactouser']}", 6)
        indent_print(f"Exporting to Grid - KW: {mix_status['pactogrid']}", 6)
