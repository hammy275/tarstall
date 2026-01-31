from __future__ import annotations  # For forward declaring type-hints (they internally become strings)
from install_type import InstallType
from typing import Union

class Program:
    """Program.

    Represents an installed program via tarstall.

    Args:
        name (str): Name of installed program. Should correspond to the folder name in ~/.tarstall/bin.
        install_type (InstallType): The method of installation the program uses.
        shortcuts (list[str]: The list of shortcuts (formerly desktops) the program has. Should be the filename, not including extension or the rest of the path.
        post_upgrade_script (str): The script to run after the program upgrades.
        update_url (str): The URL to update the program from if it's not a GIT program.
        in_path (bool): Whether the program's folder has been added to PATH.
        binlinks (list[str]): The list of binlink names the program has.
        update_archive_type (str): The file extension of the archive type that is download when updating as a DEFAULT program.

    """
    def __init__(self, name: str, install_type: InstallType = InstallType.DEFAULT,
                 shortcuts: Union[list[str], None] = None, post_upgrade_script: Union[str, None] = None,
                 update_url: Union[str, None] = None, in_path: bool = False,
                 binlinks: Union[list[str], None] = None, update_archive_type: Union[str, None] = None):
        self.name = name
        self.install_type = install_type
        self.shortcuts = [] if shortcuts is None else shortcuts
        self.post_upgrade_script = post_upgrade_script
        self.update_url = update_url
        self.in_path = in_path
        self.binlinks = binlinks
        self.update_archive_type = update_archive_type

    @staticmethod
    def from_dict(name: str, dict_in: dict) -> Program:
        install_type = dict_in.get("install_type", InstallType.DEFAULT)
        shortcuts = dict_in.get("shortcuts", None)
        post_upgrade_script = dict_in.get("post_upgrade_script", None)
        update_url = dict_in.get("update_url", None)
        in_path = dict_in.get("in_path", False)
        binlinks = dict_in.get("binlinks", None)
        update_archive_type = dict_in.get("update_archive_type", None)
        return Program(name, install_type, shortcuts, post_upgrade_script, update_url, in_path, binlinks, update_archive_type)

    def to_dict(self) -> dict:
        return {
            "install_type": self.install_type.value,
            "shortcuts": self.shortcuts,
            "post_upgrade_script": self.post_upgrade_script,
            "update_url": self.update_url,
            "in_path": self.in_path,
            "binlinks": self.binlinks,
            "update_archive_type": self.update_archive_type
        }

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
