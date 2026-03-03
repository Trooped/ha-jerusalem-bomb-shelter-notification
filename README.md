# ha-jerusalem-bomb-shelter-notification

A HA script with a notification to your phone with the 3 closest bomb shelters to your current location. 

This project is built specifically using the Jerusalem municipality's shelter dataset, but it can be adapted to any city by modifying the CSV file. It actively pings your phone for fresh GPS coordinates so you always get the closest shelters, whether you are at home or out and about.

## Table of Contents
- [Requirements](#requirements)
- [Step 1: The CSV Data](#step-1-the-csv-data)
- [Step 2: The Python Script](#step-2-the-python-script)
- [Step 3: Configure the Shell Command](#step-3-configure-the-shell-command)
- [Step 4: Create the Home Assistant Script](#step-4-create-the-home-assistant-script)
- [Step 5: Use The Script However You Want](#step-5-use-the-script-however-you-want)

## Requirements
- Home Assistant
- Smartphone with the Home Assistant Companion App installed.
- Location Permissions granted to the Home Assistant app on your phone (and a person.YOURNAME entity with your location).
  - **Android Users:** Ensure the HA app is excluded from battery optimization so it wakes up instantly when the location is requested.
  - **iOS Users:** Ensure Location Permissions are set to **"Always"** with **"Precise Location"** turned ON. **Background App Refresh** must also be enabled.
- A CSV file containing shelter data (`Records.csv`).
- Preferably - Google Maps app on your phone.

## Step 1: The CSV Data
You need a list of public shelters with their coordinates. Jerusalem has an extensive list which I'll be using here. 
1. Get your `Records.csv` file. Ensure it has columns named exactly:
   - `קואורדינטות ציר x` (Latitude)
   - `קורדינטות ציר y` (Longitude)
   - `כתובת` (Address)
   
   **Or, alternatively** - edit the find_shelters.py file to support your csv file's fields and name.
   
2. If you live in Jerusalem, you can just take the `Records.csv` file from this repo.
3. Upload `Records.csv` (or your other file) directly into your Home Assistant `/config` directory.

## Step 2: The Python Script
We use a lightweight Python script to calculate the Haversine distance between your live coordinates and all the shelters in the CSV file, outputting the results as JSON.

1. Take the `find_shelters.py` file from this repo and upload it into your Home Assistant `/config` directory.
2. If you need the file name/variable names - do it now.


## Step 3: Configure the Shell Command
Home Assistant needs permission to run the Python script and pass it your live coordinates from your person entity.

1. Open your `configuration.yaml` file.
2. Add your shell command configuration somewhere in the file:

```yaml
shell_command:
  get_nearest_shelters: "python3 /config/find_shelters.py {{ lat }} {{ lon }}"
```

3. **Restart Home Assistant** to apply the new shell command and ensure the files you uploaded are valid and recognized by HA.

## Step 4: Create the Home Assistant Script
This sequence wakes up your phone's GPS using an invisible notification, waits 5 seconds for a fresh location update to hit the server, runs the math using your `person.YOURNAME` entity, and sends an actionable push notification to your phone with 3 clickable Google Maps buttons.

1. Go to Settings > Automations & Scenes > Scripts.
2. Click Add Script and choose Edit in YAML.
3. Paste the following script and make sure to change your notification and person entity to your specific ones:

```yaml
alias: Send Nearest Shelters
description: Finds nearest shelters using live location and sends actionable notification
sequence:
  - action: notify.YOUR_COMPANION_APP
    metadata: {}
    data:
      message: request_location_update
  - delay:
      hours: 0
      minutes: 0
      seconds: 5
      milliseconds: 0
  - action: shell_command.get_nearest_shelters
    data:
      lat: "{{ state_attr('person.YOURNAME', 'latitude') }}"
      lon: "{{ state_attr('person.YOURNAME', 'longitude') }}"
    response_variable: shelter_data
  - variables:
      shelters: "{{ (shelter_data['stdout'] | from_json).shelters }}"
  - action: notify.YOUR_COMPANION_APP
    metadata: {}
    data:
      title: 🚨 מקלטים קרובים
      data:
        channel: alarm_stream
        priority: high
        ttl: 0
        color: red
        tag: critical_alert
        sticky: true
        actions:
          - action: URI
            title: "{{ shelters[0].address }} ({{ shelters[0].distance }}m)"
            uri: "{{ shelters[0].url }}"
          - action: URI
            title: "{{ shelters[1].address }} ({{ shelters[1].distance }}m)"
            uri: "{{ shelters[1].url }}"
          - action: URI
            title: "{{ shelters[2].address }} ({{ shelters[2].distance }}m)"
            uri: "{{ shelters[2].url }}"
      message: הנה 3 המקלטים הקרובים ביותר אליך (משמאל לימין)
mode: single
```

## Step 5: Use The Script However You Want
Here are some use cases:
1. Automate this script based on [oref_alert integration by @amitfin](https://github.com/amitfin/oref_alert)
2. Create a button that calls this script.
