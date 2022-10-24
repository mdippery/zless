from pathlib import Path

import pytest

from zless.paths import output_path, to_path


@pytest.mark.parametrize(
    "input_path,output_path",
    [
        (__file__, Path(__file__)),
        (Path(__file__), Path(__file__)),
    ],
)
def test_conversion_of_path(input_path, output_path):
    actual = to_path(input_path)
    assert actual == output_path


@pytest.mark.parametrize(
    "source,dest,expected",
    [
        ("zless-22.1.dev0/PKG-INFO", "/tmp/PKG-INFO", Path("/tmp/PKG-INFO")),
        ("zless-22.1.dev0/PKG-INFO", "/tmp/blah", Path("/tmp/blah")),
        ("zless-22.1.dev0/PKG-INFO", "/tmp/", Path("/tmp/PKG-INFO")),
        ("zless-22.1.dev0/PKG-INFO", "/tmp", Path("/tmp/PKG-INFO")),
    ],
)
def test_calculation_of_output_path(source, dest, expected):
    actual = output_path(source, dest)
    assert actual == expected
