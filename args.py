#!/usr/bin/python3

import os
import sys
import config
import shlex

arguments = []
parsed_args = []

MAX_PRIORITY = 10

# Core Argument Class
class Argument:
    """Argument Class.

    Represents an argument for the command line.

    """
    def __init__(self, arg_short, arg_long, arg_desc, desc, priority, dont_add=False):
        """Init Argument.

        Args:
            arg_short (str): Shorthand argument. 'v' in VerboseArgument's case.
            arg_long (str): Longhand argument. 'install' for InstallArgument's case.
            arg_desc (str): Argument description for help. [PROGRAM] to get `-i/--install [PROGRAM]` for install.
            desc (str): Short description describing what the argument does
            priority (int): Priority to execute this argument in. The closer to 1, the sooner to execute.
            dont_add (bool): Don't add to arguments list
        """
        self.arg_short = arg_short
        self.arg_long = arg_long
        self.arg_desc = arg_desc
        self.desc = desc
        self.priority = priority
        # Holds value from argument. Set to True if the argument doesn't take anything extra but is present.
        self.val = None

        if not dont_add:
            arguments.append(self)

    def arg_count(self, argv):
        """Get Arguments from argv.

        Args:
            argv (str[]): List of all arguments following this argument. For example, 'tarstall -i program -v'
            would pass ["program", "-v"] to the InstallArgument

        Returns:
            int: An int representing the number of arguments to capture for this argument.
        """
        return 0

    def get_next(self, argv):
        """Get Next for Tab Completion.

        Gets the tab completion based on the state of argv.

        Args:
            argv (str[]): See arg_count's argv.

        Returns:
            str[]: List of arguments that can be used to tab complete the last argument in argv
        """
        return []

# Abstract Arguments


class ProgramArgument(Argument):

    def __init__(self, arg_short, arg_long, arg_desc, desc, priority, dont_add=False):
        super().__init__(arg_short, arg_long, arg_desc, desc, priority, dont_add)

    def arg_count(self, argv):
        return 1

    def get_next(self, argv):
        if len(argv) == 1:
            prog = argv[0]
            progs = []
            if "programs" in config.db:
                for program in config.db["programs"].keys():
                    if program.lower().startswith(prog):
                        progs.append(program)
                return progs
        elif "programs" in config.db:
            return list(config.db["programs"].keys())

# Actual Arguments


class HelpArgument(Argument):
    def __init__(self):
        super().__init__("h", "help", "", "Displays this help prompt", MAX_PRIORITY)


class InstallArgument(Argument):
    def __init__(self):
        super().__init__("i", "install", "[ARCHIVE/DIRECTORY/FILE/URL]",
                         "Installs the supplied archive/directory/file/git URL/archive URL", MAX_PRIORITY)

    def arg_count(self, argv):
        return 1

    def get_next(self, argv):
        files = []
        if len(argv) > 0:
            path = argv[0]
        else:
            path = ""
        paths = path.split("/")
        search = paths[len(paths) - 1].lower()
        dir = os.getcwd()
        if len(paths) > 1:
            dir = os.path.join(os.getcwd(), "/".join(search[:-1]))
        for file in os.listdir(dir):
            if file.lower().startswith(search):
                files.append(shlex.quote(os.path.join(dir, file)))

        return files


class NameArgument(Argument):
    def __init__(self):
        super().__init__("n", "name", "[NAME]",
                         "Specify a name for the program manually. Required if installing an archive URL.", 2)

    def arg_count(self, argv):
        return 1


class RemoveArgument(ProgramArgument):
    def __init__(self):
        super().__init__("r", "remove", "[PROGRAM]", "Uninstalls [PROGRAM] from tarstall", MAX_PRIORITY)


class ListArgument(Argument):
    def __init__(self):
        super().__init__("l", "list", "", "Lists all installed programs", MAX_PRIORITY)


class FirstInstallArgument(Argument):
    def __init__(self):
        super().__init__("f", "first", "", "Runs first-time setup", MAX_PRIORITY)


class EraseArgument(Argument):
    def __init__(self):
        super().__init__("e", "erase", "", "Removes tarstall from your system", MAX_PRIORITY)


class VerboseArgument(Argument):
    def __init__(self):
        super().__init__("v", "verbose", "", "Enables verbose mode for this run of tarstall", 1)


class UpdateTarstallArgument(Argument):
    def __init__(self):
        super().__init__("u", "update", "", "Updates tarstall if an update is available", MAX_PRIORITY)


class ManageProgramArgument(ProgramArgument):
    def __init__(self):
        super().__init__("m", "manage", "[PROGRAM]", "Manage the program named [PROGRAM]", MAX_PRIORITY)


class RemoveLockArgument(Argument):
    def __init__(self):
        super().__init__("k", "remove-lock", "",
                         "Removes tarstall's lock (only do this if tarstall isn't already running)", 3)


class ConfigArgument(Argument):
    def __init__(self):
        super().__init__("c", "config", "", "Configure tarstall", MAX_PRIORITY)


class UpgradeArgument(Argument):

    def __init__(self):
        super().__init__("q", "update-programs", "[PROGRAM]",
                         "Updates [PROGRAM], or all programs if [PROGRAM] is not specified", MAX_PRIORITY)
        self.prog_argument = ProgramArgument(None, None, None, None, None, dont_add=True)

    def arg_count(self, argv):
        if len(argv) == 0:
            return 0
        else:
            return self.prog_argument.arg_count(argv)

    def get_next(self, argv):
        extra = [""] if len(argv) == 0 else []
        return list(self.prog_argument.get_next(argv)) + extra


# Internal API Functions

def get_matching_argument(arg, priority=None):
    """Get Matching Argument.

    Get Argument object for incoming arg

    Args:
        arg (str): Argument to get argument object for
        priority (int): Priority to filter by, or None if priority isn't cared for.

    Returns:
        Argument: Argument object based on arg
    """
    while arg.startswith("-"):
        arg = arg[1:]
    for argument in arguments:
        if (argument.arg_short == arg or argument.arg_long == arg) and \
                (priority is None or argument.priority == priority):
            return argument
    return None


def parse_args(argv):
    """Parse Arguments.

    Parse arguments for execution, and store them in parsed_args.

    Args:
        argv (str[]): Raw list of arguments from sys.argv
    """
    parsed_args.clear()
    args = []
    for arg in argv:  # Copy argv
        args.append(arg)
    args = args[1:]  # Chop off tarstall call
    for priority in range(MAX_PRIORITY + 1):
        for arg_index in range(len(args)):
            arg = get_matching_argument(args[arg_index], priority)
            if arg is not None:
                count = arg.arg_count(args[arg_index + 1:])
                if count == 0:
                    arg.val = True
                else:
                    arg.val = args[arg_index + 1:arg_index + 1 + count]  # Get arguments
                parsed_args.append(arg)
                break
    return True


def get_tab_complete(argv):
    """Get Tab Completion.

    Get the tab completion for incoming arguments.

    Args:
        argv (str[]): List of arguments from sys.argv

    Returns:
        str[]: List of possible autocompletes. Can be empty!
    """
    args = []
    for arg in argv:  # Copy argv
        args.append(arg)
    args = args[2:]  # Chop off args.py and tarstall call
    while len(args) > 0:
        argument = get_matching_argument(args[0])
        if argument is not None:
            count = argument.arg_count(args)
            if len(args) - count - 1 <= 0:
                # Do tab completion, we're at our last argument!
                return argument.get_next(args[1:])
            else:
                args = args[1 + count:]
        else:
            args = args[1:]
    return []

help_arg = HelpArgument()
install_arg = InstallArgument()
name_arg = NameArgument()
remove_arg = RemoveArgument()
list_arg = ListArgument()
first_install_arg = FirstInstallArgument()
erase_arg = EraseArgument()
verbose_arg = VerboseArgument()
update_tarstall_arg = UpdateTarstallArgument()
manage_program_arg = ManageProgramArgument()
remove_lock_arg = RemoveLockArgument()
config_arg = ConfigArgument()
upgrade_arg = UpgradeArgument()


if __name__ == "__main__":
    completes = get_tab_complete(" ".join(sys.argv).split(" "))
    sys.stdout.write(" ".join(completes))
    sys.stdout.flush()
