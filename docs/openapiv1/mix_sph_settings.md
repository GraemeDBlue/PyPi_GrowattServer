# MIX/SPH Inverter Settings

This is part of the [OpenAPI V1 doc](../openapiv1.md).

For MIX/SPH systems, the public V1 API provides a way to read and write inverter settings:

* **Device Settings**
  * function: `api.device_settings`
  * parameters:
    * `device_sn`: The device serial number
    * `device_type`: Use `DeviceType.SPH_MIX` for MIX/SPH inverters

* **Read Parameter**
  * function: `api.read_parameter`
  * parameters:
    * `device_sn`: The device serial number
    * `device_type`: Use `DeviceType.SPH_MIX` for MIX/SPH inverters
    * `parameter_id`: Parameter ID to read (e.g., "ac_charge", "discharge_power")

* **Time Segments**
  * function: `api.read_time_segments`
  * parameters:
    * `device_sn`: The device serial number
    * `device_type`: Use `DeviceType.SPH_MIX` for MIX/SPH inverters
    * `settings_data`: Optional settings data to avoid redundant API calls

  Returns:
    ```python
    [
        {
            'segment_id': int,  # Segment number (1-9)
            'batt_mode': int,   # 0=Load First, 1=Battery First, 2=Grid First
            'mode_name': str,   # String representation of the mode
            'start_time': str,  # Start time in format "HH:MM"
            'end_time': str,    # End time in format "HH:MM"
            'enabled': bool     # Whether the segment is enabled
        },
        # ... (up to 9 segments)
    ]
    ```

## Common Usage Examples

### Reading Device Settings
```python
from growattServer import OpenApiV1, DeviceType

api = OpenApiV1(token="your_api_token")
settings = api.device_settings("DEVICE_SN", DeviceType.SPH_MIX)
```

### Reading Parameters
```python
# Read a specific parameter
value = api.read_parameter("DEVICE_SN", DeviceType.SPH_MIX, "ac_charge")
```

### Reading Time Segments
```python
# Option 1: Single call
segments = api.read_time_segments("DEVICE_SN", DeviceType.SPH_MIX)

# Option 2: Reuse settings data to avoid multiple API calls
settings = api.device_settings("DEVICE_SN", DeviceType.SPH_MIX)
segments = api.read_time_segments("DEVICE_SN", DeviceType.SPH_MIX, settings)