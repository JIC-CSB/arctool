"""Test the arctool package."""


def test_version_is_string():
    import arctool
    assert isinstance(arctool.__version__, str)
