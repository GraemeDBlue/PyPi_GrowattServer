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
    * `parameter_id`: Parameter ID to read (e.g., "pv_on_off", "mix_ac_discharge_time_period")


List:
  mix_ac_discharge_time_period
	mix_ac_charge_time_period	
  backflow_setting	
  pv_on_off	
  pf_sys_year	
  pv_grid_voltage_high	
  pv_grid_voltage_low	
  mix_off_grid_enable	
  mix_ac_discharge_frequency	
  mix_ac_discharge_voltage	
  v_reactive_p_rate	
  pv_power_factor	
  mix_load_flast_value_multi	
  mix_load_first_control	
  mix_single_export


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

* **Write Time Segment**
  * function: `api.write_time_segment`
  * parameters:
    * `device_sn`: The device serial number
    * `device_type`: Use `DeviceType.SPH_MIX` for MIX/SPH inverters
    * `settings_data`: Optional settings data to avoid redundant API calls

  Returns:
    ```python
    []
    ```    

| Parameter name | Grid priority setting item   | Battery priority setting item   | Anti-backflow setting item                 | Set power on and off  | Set time                                        | Set the upper limit of mains voltage | Set the lower limit of mains voltage | Set off-grid enable       | Set off-grid frequency     | Setting Off-grid voltage  | Set whether to store the following PF commands | Set active power | Set reactive power         | Set PF value           | Discharge stop SOC | LoadFirst three-phase independent output                                                                            | Single-phase anti-reverse flow | Parameter description |
|----------------|------------------------------|---------------------------------|--------------------------------------------|-----------------------|-------------------------------------------------|--------------------------------------|--------------------------------------|---------------------------|----------------------------|---------------------------|------------------------------------------------|------------------|----------------------------|------------------------|--------------------|---------------------------------------------------------------------------------------------------------------------|--------------------------------|-----------------------|
| type           | mix_ac_discharge_time_period | mix_ac_charge_time_period       | backflow_setting                           | pv_on_off             | pf_sys_year                                     | pv_grid_voltage_high                 | pv_grid_voltage_low                  | mix_off_grid_enable       | mix_ac_discharge_frequency | mix_ac_discharge_voltage  | v_reactive_p_rate                              | pv_power_factor  | mix_load_flast_value_multi | mix_load_first_control | mix_single_export  | The parameter description is inside the brackets, and the parameter list is outside the brackets or parameter range |
| param1         | 0~100 (discharge power)      | 0~100 (charging power)          | 1 (on), 0 (off)                            | 0000 (off), 0001 (on) | 00 (hour): 00 (minute) ~ 00 (hour): 00 (minute) | 270                                  | 180                                  | 1 (enabled), 0 (disabled) | 0 (50HZ), 1 (60HZ)         | 0 (230), 1 (208), 2 (240) | 1 (on), 0 (off)                                | 0~100            | 0~100                      | -0.8 ~ -1/0.8 ~ 1      | 0~100              | 0 (three-phase sum enable), 1 (single phase enable)                                                                 | 0( off),1(on)                  |                       |
| param2         | 0~100 (discharge stop SOC)   | 0~100 (charge stop SOC)         | 0~100 (anti-reverse flow power percentage) |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param3         | 00~23 (hour)                 | 1 (enable), 0 (disable) (mains) |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |
| param4         | 00~59 (minutes)              | 00~23 (hours)                   |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param5         | 00~23 (hours)                | 00~59 (minutes)                 |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param6         | 00~59 (minutes)              | 00~23 (hours)                   |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param7         | 1 (enable), 0 (disable)      | 00~59 (minutes)                 |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |
| param8         | 00~23 (hour)                 | 1 (enable), 0 (disable)         |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |
| param9         | 00~59 (minutes)              | 00~23 (hours)                   |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param10        | 00~23 (hours)                | 00~59 (minutes)                 |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param11        | 00~59 (minutes)              | 00~23 (hours)                   |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param12        | 1 (enable), 0 (disable)      | 00~59 (minutes)                 |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |
| param13        | 00~23 (hour)                 | 1 (enabled), 0 (disabled)       |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |
| param14        | 00~59 (minutes)              | 00~23 (hours)                   |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param15        | 00~23 (hours)                | 00~59 (minutes)                 |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param16        | 00~59 (minutes)              | 00~23 (hours)                   |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |
| param17        | 1 (enable), 0 (disable)      | 00~59 (minutes)                 |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |
| param18        |                              | 1 (enabled), 0 (disabled)       |                                            |                       |                                                 |                                      |                                      |                           |                            |                           |                                                |                  |                            |                        |                    |                                                                                                                     |                                |                       |







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