import pytest

from ubireader.ubifs.output import is_safe_path


@pytest.mark.parametrize(
    "basedir, path, expected",
    [
        ("/lib/out", "/lib/out/file", True),
        ("/lib/out", "file", True),
        ("/lib/out", "dir/file", True),
        ("/lib/out", "some/dir/file", True),
        ("/lib/out", "some/dir/../file", True),
        ("/lib/out", "some/dir/../../file", True),
        ("/lib/out", "some/dir/../../../file", False),
        ("/lib/out", "some/dir/../../../", False),
        ("/lib/out", "some/dir/../../..", False),
        ("/lib/out", "../file", False),
        ("/lib/out", "/lib/out/../file", False),
        ("/lib/out", "../out_hack", False),
        ("/lib/out", "../outx", False),
        ("/lib/out", "../out.bak/file", False),
        ("/lib/out", "/lib/out_hack", False),
        ("/lib/out", "/lib/outfile", False),
        ("/lib/out", "some/dir/../../../out_hack/file", False),
    ],
)
def test_is_safe_path(basedir, path, expected):
    assert is_safe_path(basedir, path) is expected
