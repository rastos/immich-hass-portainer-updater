from custom_components.immich_update_tracker.api import ImmichUpdateClient


def test_extract_current_version_from_semver_dict():
    data = {"major": 1, "minor": 130, "patch": 2}
    assert ImmichUpdateClient.extract_current_version(data) == "1.130.2"


def test_extract_current_version_from_string_dict():
    data = {"version": "v1.130.2"}
    assert ImmichUpdateClient.extract_current_version(data) == "1.130.2"


def test_extract_latest_version_nested():
    data = {"info": {"latestVersion": "v1.131.0"}}
    assert ImmichUpdateClient.extract_latest_version(data) == "1.131.0"


def test_extract_update_available_nested():
    data = {"state": {"updateAvailable": True}}
    assert ImmichUpdateClient.extract_update_available(data) is True
