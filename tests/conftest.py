import pytest

import prog_manage
from io import StringIO


@pytest.fixture(autouse=True)
def pre_test(monkeypatch):
    assert prog_manage.erase() == "Erased" or prog_manage.erase() == "Not installed"

    prog_manage.first_time_setup()

    prog_manage.verbose_toggle()

    monkeypatch.setattr('sys.stdin', StringIO("n\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\nn\n"))
    prog_manage.install("./tests/fake_packages/package.tar.gz")