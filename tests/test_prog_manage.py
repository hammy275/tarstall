import pytest
import os
from io import StringIO

import prog_manage
import config
import tarstall_manage

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


def test_gitinstall(monkeypatch):
    monkeypatch.setattr(prog_manage, "finish_install", nothing_two)
    prog_manage.gitinstall("https://github.com/hammy3502/tarstall.git", "tarstall")
    assert os.path.isfile(os.path.expanduser("~/.tarstall/bin/tarstall/prog_manage.py"))


def test_get_file_version():
    assert tarstall_manage.get_file_version("prog") == config.prog_internal_version
    assert tarstall_manage.get_file_version("file") == config.file_version


def test_pathify():
    prog_manage.pathify("package")
    assert config.check_line("export PATH=$PATH:~/.tarstall/bin/package # package", "~/.tarstall/.bashrc", "fuzzy")


def test_verbose_toggle():
    tarstall_manage.verbose_toggle()
    assert config.read_config("Verbose") is False
    tarstall_manage.verbose_toggle()
    assert config.read_config("Verbose") is True


def test_list_programs(capsys):
    prog_manage.list_programs() == ["package"]


def test_create_desktop(monkeypatch):
    prog_manage.create_desktop("package", "Name", "test.sh", "Comment here", "False")
    assert config.exists("~/.local/share/applications/tarstall/test.sh-package.desktop")


def test_remove_desktop():
    prog_manage.create_desktop("package", "Name", "test.sh", "Comment here", "False")
    try:
        assert config.exists("~/.local/share/applications/tarstall/test.sh-package.desktop")
    except AssertionError:
        print("create_desktop() failure, remove_desktop() might be okay.")
    prog_manage.remove_desktop("package", "test.sh-package")
    assert not config.exists("~/.local/share/applications/tarstall/test.sh-package.desktop")


def test_uninstall():
    prog_manage.uninstall("package")
    assert config.check_line("export PATH=$PATH:~/.tarstall/bin/package # package", "~/.tarstall/.bashrc",
                           "fuzzy") is False
    assert os.path.isfile(config.full("~/.tarstall/bin/package/test.sh")) is False


def test_install(monkeypatch):
    os.chdir(os.path.realpath(__file__)[:-19])
    monkeypatch.setattr(prog_manage, "finish_install", nothing_two)
    prog_manage.install("./fake_packages/package.tar.gz")
    assert os.path.isfile(os.path.expanduser("~/.tarstall/bin/package/test.sh"))


def test_repair_db():
    tarstall_manage.repair_db()
    assert config.db["programs"]["package"]["install_type"] == "single"  # Since the archive only contains one file, it gets re-detected as single-file


def test_create_db():
    tarstall_manage.create_db()
    #TODO: Fake os so we can test get_shell_file in any environment
    assert config.db == {
        "options": {
            "Verbose": False,
            "AutoInstall": False,
            "ShellFile": config.get_shell_file(),
            "SkipQuestions": False,
            "UpdateURLPrograms": False,
            "PressEnterKey": True
        },
        "version": {
            "file_version": config.file_version,
            "prog_internal_version": config.prog_internal_version,
            "branch": "master"
        },
        "programs": {
        }
    }


def test_erase():
    assert tarstall_manage.erase() == "Erased"
    assert os.path.isfile(config.full("~/.tarstall/tarstall.py")) is False
    try:
        assert config.check_line("source ~/.tarstall/.bashrc", "~/.bashrc", "fuzzy") is False
    except FileNotFoundError:
        try:
            config.check_line("source ~/.tarstall/.zshrc", "~/.zshrc", "fuzzy") is False
        except FileNotFoundError:
            raise AssertionError("Please use bash or zsh for testing!")
