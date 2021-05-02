import pytest

import prog_manage
from io import StringIO

import tarstall_manage


@pytest.fixture(autouse=True)
def pre_test(monkeypatch):
    assert tarstall_manage.erase() == "Erased" or tarstall_manage.erase() == "Not installed"

    tarstall_manage.first_time_setup()

    tarstall_manage.verbose_toggle()

    monkeypatch.setattr('sys.stdin', StringIO("n\n"*3))
    prog_manage.install("./tests/fake_packages/package.tar.gz")