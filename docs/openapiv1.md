# OpenAPI V1

This version of the API follows the newer [OpenAPI V1 API](https://www.showdoc.com.cn/262556420217021/0) Growatt has made available.

It extends our ["Legacy" ShinePhone](./shinephone.md) so methods from [there](./shinephone.md#methods) should be available, but it's safer to rely on the functions described in this file where possible.

## Usage

The public v1 API requires token-based authentication

```python
import growattServer

api = growattServer.OpenApiV1(token="YOUR_API_TOKEN")
# Get a list of growatt plants.
plants = api.plant_list_v1()
print(plants)
```

## Methods and Variables

### Methods

Any methods that may be useful.

| Method | Arguments | Description |
|:---|:---|:---|
| `api.plant_list()` | None | Get a list of plants registered to your account. |
| `api.plant_details(plant_id)` | plant_id: String | Get detailed information about a power station. |
| `api.plant_energy_overview(plant_id)` | plant_id: String | Get energy overview data for a plant. |
| `api.plant_energy_history(plant_id, start_date, end_date, time_unit, page, perpage)` | plant_id: String, start_date: Date, end_date: Date, time_unit: String, page: Int, perpage: Int | Get historical energy data for a plant for multiple days/months/years. |
| `api.device_list(plant_id)` | plant_id: String | Get a list of devices in specified plant. |
| `api.min_energy(device_sn)` | device_sn: String | Get current energy data for a min inverter, including power and energy values. |
| `api.min_detail(device_sn)` | device_sn: String | Get detailed data for a min inverter. |
| `api.min_energy_history(device_sn, start_date=None, end_date=None, timezone=None, page=None, limit=None)` | device_sn: String, start_date: Date, end_date: Date, timezone: String, page: Int, limit: Int | Get energy history data for a min inverter (7-day max range). |
| `api.min_settings(device_sn)` | device_sn: String | Get all settings for a min inverter. |
| `api.min_read_parameter(device_sn, parameter_id, start_address=None, end_address=None)` | device_sn: String, parameter_id: String, start_address: Int, end_address: Int | Read a specific setting for a min inverter. see: [details](./openapiv1/min_tlx_settings.md) |
| `api.min_write_parameter(device_sn, parameter_id, parameter_values)` | device_sn: String, parameter_id: String, parameter_values: Dict/Array | Set parameters on a min inverter. Parameter values can be a single value, a list, or a dictionary. see: [details](./openapiv1/min_tlx_settings.md) |
| `api.min_write_time_segment(device_sn, segment_id, batt_mode, start_time, end_time, enabled=True)` | device_sn: String, segment_id: Int, batt_mode: Int <0=load priority, 1=battery priority, 2=grid priority>, start_time: Time, end_time: Time, enabled: Bool | Update a specific time segment for a min inverter. see: [details](./openapiv1/min_tlx_settings.md) |
| `api.min_read_time_segments(device_sn, settings_data=None)` | device_sn: String, settings_data: Dict | Read all time segments from a MIN inverter. Optionally pass settings_data to avoid redundant API calls. see: [details](./openapiv1/min_tlx_settings.md) |

Methods from [here](./shinephone.md#methods) should be available, but it's safer to rely on the functions described in this file where possible. There is no guarantee those methods will work, or remain stable through updates.

### Variables

Some variables you may want to set.

`api.server_url` The growatt server URL, default: 'https://openapi.growatt.com/v1/'

You may need a different URL depending on where your account is registered:

'https://openapi-cn.growatt.com/v1/' (Chinese server)
'https://openapi-us.growatt.com/v1/' (North American server)
'https://openapi.growatt.com/v1/' (Other regional server: e.g. Europe)

### Initialisation

```python
api = growattServer.GrowattApiV1(token="YOUR_API_TOKEN") # Initialize with your API token
```