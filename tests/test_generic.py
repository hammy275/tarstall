from io import StringIO

import generic

def test_get_input(monkeypatch):
    monkeypatch.setattr("sys.stdin", StringIO("y\n"))
    assert generic.get_input("question_string", ['y', 'n'], 'n') == 'y'
    monkeypatch.setattr("sys.stdin", StringIO("\n"))
    assert generic.get_input("question_string", ['y', 'n'], 'n') == 'n'
    monkeypatch.setattr("sys.stdin", StringIO("a\ny\n"))
    assert generic.get_input("question_string", ['y', 'n'], 'n') == 'y'


def test_endi():
    assert generic.endi(True) == "enabled"
    assert generic.endi(False) == "disabled"