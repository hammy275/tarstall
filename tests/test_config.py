import config
import os

import file
import prog_manage
import json

import tarstall_manage


def test_check_bin():
    assert file.check_bin("sh") is True
    assert file.check_bin("agtasdytfhgasdfsudyghaushdgj") is False


def test_replace_in_file():
    with open("/tmp/tarstall-test-temp", "w") as f:
        f.write("Test Line.")
    file.replace_in_file("Test Line.", "TestHere", "/tmp/tarstall-test-temp")
    with open("/tmp/tarstall-test-temp", "r") as f:
        assert f.readline() == "TestHere"
    
    with open("/tmp/tarstall-test-temp-two", "w") as f:
        f.write("Test Line.")
    file.replace_in_file("No Replace.", "TestHere", "/tmp/tarstall-test-temp")
    with open("/tmp/tarstall-test-temp-two", "r") as f:
        assert f.readline() == "Test Line."
    os.remove("/tmp/tarstall-test-temp-two")
    os.remove("/tmp/tarstall-test-temp")


def test_read_config():
    assert config.read_config("Verbose") is True


def test_change_config():
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is False
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is True


def test_vcheck():
    assert config.vcheck() is True


def test_lock():
    file.lock()
    assert os.path.isfile("/tmp/tarstall-lock")


def test_locked():
    assert file.locked() == os.path.isfile("/tmp/tarstall-lock")


def test_unlock():
    file.unlock()
    assert not os.path.isfile("/tmp/tarstall-lock")

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


def test_name():
    assert file.name("/some/directory/config.tar.gz") == "config"
    assert file.name("~/i/was/home/but/now/im/here.zip") == "here"
    assert file.name("./tar/xz/files/are/pretty/cool.tar.xz") == "cool"


def test_extension():
    assert file.extension("weeeeee.zip") == ".zip"
    assert file.extension("asdf.tar.gz") == ".tar.gz"
    assert file.extension("aconfig.7z") == ".7z"
    assert file.extension("this_is_a_file.that.is.cool.tar.xz") == ".tar.xz"


def test_exists():
    assert file.exists(os.path.expanduser("~/.tarstall/config.py")) is True
    assert file.exists("./config.no") is False


def test_spaceify():
    assert file.spaceify("this is a test") == "this\\ is\\ a\\ test"


def test_check_line():
    # TODO: Test other modes
    file.create("~/.tarstall/config")
    file.add_line("Test Line", "~/.tarstall/config")
    assert file.check_line("Test Line", "~/.tarstall/config", "fuzzy") is True
    assert file.check_line("ThisShouldNotBeFound=True", "~/.tarstall/config", "fuzzy") is False


def test_create():
    file.create("~/.tarstall/test01")
    assert file.exists("~/.tarstall/test01")


def test_remove_line():
    # TODO: Test other modes
    file.create("~/.tarstall/config")
    file.add_line("Test Line", "~/.tarstall/config")
    file.add_line("Verbose=True", "~/.tarstall/config")
    file.remove_line("Test Line", "~/.tarstall/config", "fuzzy")
    assert file.check_line("Verbose=False", "~/.tarstall/config", "fuzzy") is False


def test_add_line():
    file.add_line("Verbose=False\n", "~/.tarstall/config")
    assert file.check_line("Verbose=False", "~/.tarstall/config", "fuzzy") is True


def test_char_check():
    assert file.char_check("asdf") is False
    assert file.char_check("asdf ") is True
    assert file.char_check("as#df") is True


def test_write_db():
    old_db = config.db
    tarstall_manage.update({"test": "here"})
    config.write_db()
    tarstall_manage.update({"test": "here"})
    with open(file.full("~/.tarstall/database")) as f:
        db = json.load(f)
    assert old_db == db
