import config
import os
import prog_manage
import json


def test_check_bin():
    assert config.check_bin("sh") is True
    assert config.check_bin("agtasdytfhgasdfsudyghaushdgj") is False


def test_replace_in_file():
    with open("/tmp/tarstall-test-temp", "w") as f:
        f.write("Test Line.")
    config.replace_in_file("Test Line.", "TestHere", "/tmp/tarstall-test-temp")
    with open("/tmp/tarstall-test-temp", "r") as f:
        assert f.readline() == "TestHere"
    
    with open("/tmp/tarstall-test-temp-two", "w") as f:
        f.write("Test Line.")
    config.replace_in_file("No Replace.", "TestHere", "/tmp/tarstall-test-temp")
    with open("/tmp/tarstall-test-temp-two", "r") as f:
        assert f.readline() == "Test Line."
    os.remove("/tmp/tarstall-test-temp-two")
    os.remove("/tmp/tarstall-test-temp")


def test_read_config():
    assert config.read_config("Verbose") is False


def test_change_config():
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is True
    config.change_config("Verbose", "flip")
    assert config.read_config("Verbose") is False


def test_vcheck():
    assert config.vcheck() is False


def test_lock():
    config.lock()
    assert os.path.isfile("/tmp/tarstall-lock")


def test_locked():
    assert config.locked() == os.path.isfile("/tmp/tarstall-lock")


def test_unlock():
    config.unlock()
    assert not os.path.isfile("/tmp/tarstall-lock")

def test_get_db():
    assert config.get_db() == {
        "options": {
            "Verbose": False,
            "AutoInstall": False,
            "ShellFile": config.get_shell_file(),
            "SkipQuestions": False,
            "UpdateURLPrograms": False
        },
        "version": {
            "file_version": config.file_version,
            "prog_internal_version": config.prog_internal_version,
            "branch": "master"
        },
        "programs": {
            "package": {
                "git_installed": False,
                "desktops": [],
                "post_upgrade_script": None,
                "update_url": None,
                "has_path": False,
                "binlinks": []
            }
        }
    }


def test_name():
    assert config.name("/some/directory/config.tar.gz") == "config"
    assert config.name("~/i/was/home/but/now/im/here.zip") == "here"
    assert config.name("./tar/xz/files/are/pretty/cool.tar.xz") == "cool"


def test_extension():
    assert config.extension("weeeeee.zip") == ".zip"
    assert config.extension("asdf.tar.gz") == ".tar.gz"
    assert config.extension("aconfig.7z") == ".7z"
    assert config.extension("this_is_a_file.that.is.cool.tar.xz") == ".tar.xz"


def test_exists():
    assert config.exists(os.path.expanduser("~/.tarstall/config.py")) is True
    assert config.exists("./config.no") is False


def test_spaceify():
    assert config.spaceify("this is a test") == "this\\ is\\ a\\ test"


def test_check_line():
    # TODO: Test other modes
    config.create("~/.tarstall/config")
    config.add_line("Test Line", "~/.tarstall/config")
    assert config.check_line("Test Line", "~/.tarstall/config", "fuzzy") is True
    assert config.check_line("ThisShouldNotBeFound=True", "~/.tarstall/config", "fuzzy") is False


def test_create():
    config.create("~/.tarstall/test01")
    assert config.exists("~/.tarstall/test01")


def test_remove_line():
    # TODO: Test other modes
    config.remove_line("Test Line", "~/.tarstall/config", "fuzzy")
    assert config.check_line("Verbose=False", "~/.tarstall/config", "fuzzy") is False


def test_add_line():
    config.add_line("Verbose=False\n", "~/.tarstall/config")
    assert config.check_line("Verbose=False", "~/.tarstall/config", "fuzzy") is True


def test_char_check():
    assert config.char_check("asdf") is False
    assert config.char_check("asdf ") is True
    assert config.char_check("as#df") is True


def test_write_db():
    old_db = config.db
    config.db.update({"test": "here"})
    config.write_db()
    old_db.update({"test": "here"})
    with open(config.full("~/.tarstall/database")) as f:
        db = json.load(f)
    assert old_db == db
