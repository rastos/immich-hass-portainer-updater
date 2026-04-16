from __future__ import annotations

DOMAIN = "immich_update_tracker"

CONF_NAME = "name"
CONF_IMMICH_URL = "immich_url"
CONF_IMMICH_API_KEY = "immich_api_key"
CONF_UPDATE_WEBHOOK_URL = "update_webhook_url"
CONF_POLL_INTERVAL_MINUTES = "poll_interval_minutes"

DEFAULT_NAME = "Immich"
DEFAULT_POLL_INTERVAL_MINUTES = 60

ATTR_CURRENT_VERSION = "current_version"
ATTR_LATEST_VERSION = "latest_version"
ATTR_UPDATE_AVAILABLE = "update_available"
ATTR_SOURCE = "source"
ATTR_VERSION_CHECK_RAW = "version_check_raw"

SOURCE_IMMICH_API = "immich_api"
SOURCE_GITHUB = "github"
SOURCE_UNKNOWN = "unknown"
