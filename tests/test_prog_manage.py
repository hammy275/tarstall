import os

import file
import prog_manage

"""
To write tests for:
update

manage
binlink
dirinstall
get_online_version
get_file_version
download_files
"""


def nothing_two(a, b=False):
    return None


def test_install_git(monkeypatch):
    monkeypatch.setattr(prog_manage, "finish_install", nothing_two)
    prog_manage.install("https://github.com/hammy275/tarstall.git", "tarstall")
    assert os.path.isfile(os.path.expanduser("~/.tarstall/bin/tarstall/prog_manage.py"))


def test_pathify():
    prog_manage.pathify("package")
    assert file.check_line("export PATH=$PATH:~/.tarstall/bin/package # package", "~/.tarstall/.bashrc", "fuzzy")


def test_list_programs(capsys):
    assert prog_manage.list_programs() == ["package"]


def test_create_desktop(monkeypatch):
    prog_manage.create_desktop("package", "Name", "test.sh", "Comment here", "False")
    assert file.exists("~/.local/share/applications/tarstall/test.sh-package.desktop")


def test_remove_desktop():
    prog_manage.create_desktop("package", "Name", "test.sh", "Comment here", "False")
    try:
        assert file.exists("~/.local/share/applications/tarstall/test.sh-package.desktop")
    except AssertionError:
        print("create_desktop() failure, remove_desktop() might be okay.")
    prog_manage.remove_desktop("package", "test.sh-package")
    assert not file.exists("~/.local/share/applications/tarstall/test.sh-package.desktop")


def test_uninstall():
    prog_manage.uninstall("package")
    assert file.check_line("export PATH=$PATH:~/.tarstall/bin/package # package", "~/.tarstall/.bashrc",
                           "fuzzy") is False
    assert os.path.isfile(file.full("~/.tarstall/bin/package/test.sh")) is False


def test_install_archive(monkeypatch):
    os.chdir(os.path.realpath(__file__)[:-19])
    monkeypatch.setattr(prog_manage, "finish_install", nothing_two)
    prog_manage.install("./fake_packages/package.tar.gz")
    assert os.path.isfile(os.path.expanduser("~/.tarstall/bin/package/test.sh"))


