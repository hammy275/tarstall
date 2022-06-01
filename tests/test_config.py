import config

import file
import json

import tarstall_manage


def test_read_config():
    assert config.read_config("Verbose") is True


def test_change_config():
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is False
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is True


def test_vcheck():
    assert config.vcheck() is True


def test_get_db():
    assert file.get_db() == {
        "options": {
            "Verbose": True,
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
            "package": {
                "install_type": "default",
                "desktops": [],
                "post_upgrade_script": None,
                "update_url": None,
                "has_path": False,
                "binlinks": []
            }
        }
    }


def test_write_db():
    old_db = config.db
    tarstall_manage.update({"test": "here"})
    config.write_db()
    tarstall_manage.update({"test": "here"})
    with open(file.full("~/.tarstall/database")) as f:
        db = json.load(f)
    assert old_db == db
