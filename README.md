# Immich Update Tracker

-coded with perplexity on gtp5.4 with deep thinking, not yet tested

it creates entities, with correct version info, and creates button for webhook autoupdate, in theory it should work with any webhook that doesn't need authentication.

HACS-ready Home Assistant custom integration that:
- reads the current Immich version
- checks whether an update is available
- exposes the latest version
- exposes a button entity to trigger your update webhook

## Features

- Config flow UI
- Options UI
- Polling interval configurable, default 60 minutes
- Tries Immich version-check API first
- Falls back to GitHub latest release when needed
- Button entity for webhook-triggered updates
- Four entities:
  - `sensor.<name>_current_version`
  - `sensor.<name>_latest_version`
  - `binary_sensor.<name>_update_available`
  - `button.<name>_run_update`

## Installation

1. Open HACS
2. Add this repository as a custom repository
3. Category: **Integration**
4. Install **Immich Update Tracker**
5. Restart Home Assistant
6. Go to **Settings -> Devices & Services -> Add Integration**
7. Search for **Immich Update Tracker**

## Configuration

The integration asks for:
- Immich URL
- Immich API key
- Immich update webhook URL
- Polling interval in minutes, default `60`

## Notes

- Current version is fetched from Immich.
- Latest version and update availability are taken from the Immich version-check endpoint when available.
- If that endpoint does not provide enough data, the integration falls back to GitHub releases.
- The update button performs an HTTP `POST` to the configured webhook URL with a small JSON payload.

## Development

Basic tests are included under `tests/` for parsing and version comparison logic.
