# Power Outage Sensor

This custom component for Home Assistant provides two sensors that display information about planned power outages based on your ICP (Installation Control Point) number. The sensors retrieve data from the Vector Outage Reporter API and show the start time and end time of the planned outage, along with the reason for the outage.

## Installation

1. Copy the `custom_components/power_outage_info` directory to your Home Assistant's `custom_components` directory.

   or [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=ha-auckland-power-outage&owner=nzfern&category=Integration)

3. Restart Home Assistant for the changes to take effect.

## Configuration

Add the following entry to your `configuration.yaml` file:

```yaml
sensor:
  - platform: power_outage_info
    icp_number: YOUR_ICP_NUMBER

```
Replace YOUR_ICP_NUMBER  with your specific values obtained from Vector https://help.vector.co.nz/.

For example https://help.vector.co.nz/address/1002190061LC5D2 so the ICP number 1002190061LC5D2 is followed by address/ .

Restart Home Assistant to load the new component.
