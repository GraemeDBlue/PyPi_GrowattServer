#!/usr/bin/env python3
"""Simple example of using the Growatt API."""

import growattServer

api = growattServer.GrowattApi()
login_response = api.login("username", "password")
# Get a list of growatt plants.
print(api.plant_list(login_response["user"]["id"]))  # noqa: T201
