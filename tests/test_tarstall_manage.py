import os

import config
import file
import tarstall_manage


def test_get_file_version():
    assert tarstall_manage.get_file_version("prog") == config.prog_internal_version
    assert tarstall_manage.get_file_version("file") == config.file_version


def test_verbose_toggle():
    tarstall_manage.verbose_toggle()
    assert config.read_config("Verbose") is False
    tarstall_manage.verbose_toggle()
    assert config.read_config("Verbose") is True


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
            "ShellFile": file.get_shell_file(),
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
    assert os.path.isfile(file.full(f"{config.TARSTALL_DIR}/tarstall.py")) is False
    try:
        assert file.check_line(f"source {config.TARSTALL_DIR}/.bashrc", "~/.bashrc", "fuzzy") is False
    except FileNotFoundError:
        try:
            file.check_line(f"source {config.TARSTALL_DIR}/.zshrc", "~/.zshrc", "fuzzy") is False
        except FileNotFoundError:
            raise AssertionError("Please use bash or zsh for testing!")