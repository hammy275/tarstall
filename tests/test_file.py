import os

import file


def test_check_bin():
    assert file.check_bin("sh") is True
    assert file.check_bin("agtasdytfhgasdfsudyghaushdgj") is False


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


def test_char_check():
    assert file.char_check("asdf") is False
    assert file.char_check("asdf ") is True
    assert file.char_check("as#df") is True


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


def test_lock():
    file.lock()
    assert os.path.isfile("/tmp/tarstall-lock")


def test_locked():
    assert file.locked() == os.path.isfile("/tmp/tarstall-lock")


def test_unlock():
    file.unlock()
    assert not os.path.isfile("/tmp/tarstall-lock")