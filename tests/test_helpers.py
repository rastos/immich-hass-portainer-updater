from custom_components.immich_update_tracker.helpers import clean_version, is_newer_version, version_tuple


def test_clean_version():
    assert clean_version("v1.130.2") == "1.130.2"


def test_version_tuple():
    assert version_tuple("1.130.2") == (1, 130, 2)


def test_is_newer_version_true():
    assert is_newer_version("1.131.0", "1.130.2") is True


def test_is_newer_version_false():
    assert is_newer_version("1.130.2", "1.130.2") is False
