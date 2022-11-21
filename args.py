import os
import config

arguments = []

MAIN_PRIORITY = 100

# Core Argument Class
class Argument:
    """Argument Class.

    Represents an argument for the command line.

    """
    def __init__(self, arg_short, arg_long, arg_desc, desc, priority):
        """Init Argument.

        Args:
            priority (int): Priority to execute this argument in. The closer to 1, the sooner to execute.
        """
        self.arg_short = arg_short
        self.arg_long = arg_long
        self.arg_desc = arg_desc
        self.desc = desc
        self.priority = priority

    def arg_count(self, argv):
        """Get Arguments from argv.

        Args:
            argv (str[]): List of all arguments following this argument. For example, 'tarstall -i program -v'
            would pass ["program", "-v"] to the InstallArgument

        Returns:
            str/int: An int representing the number of arguments to be passed to a function or a string representing
            an error message for a bad argument.
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

    def __init__(self):
        pass

    def arg_count(self, argv):
        if len(argv) < 1:
            return "Please specify a program!"
        elif "programs" in config.db:
            if argv[0] not in config.db["programs"].keys():
                return argv[0] + " isn't an installed program!"
            return 1
        return "Invalid database state!"  # Hopefully shouldn't happen!

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
        super().__init__("h", "help", "", "Displays this help prompt", MAIN_PRIORITY)


class InstallArgument(Argument):
    def __init__(self):
        super().__init__("i", "install", "[ARCHIVE/DIRECTORY/FILE/URL]",
                         "Installs the supplied archive/directory/file/git URL/archive URL", MAIN_PRIORITY)

    def arg_count(self, argv):
        if len(argv) < 1:
            return "Please specify something to install!"
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
                files.append(os.path.join(dir, file))

        return files


class NameArgument(Argument):
    def __init__(self):
        super().__init__("n", "name", "[NAME]",
                         "Specify a name for the program manually. Required if installing an archive URL.", 2)

    def arg_count(self, argv):
        if len(argv) < 1:
            return "Name not specified!"
        return 1


class RemoveArgument(ProgramArgument):
    def __init__(self):
        super().__init__("r", "remove", "[PROGRAM]", "Uninstalls [PROGRAM] from tarstall", MAIN_PRIORITY)


class ListArgument(Argument):
    def __init__(self):
        super().__init__("l", "list", "", "Lists all installed programs", MAIN_PRIORITY)


class FirstInstallArgument(Argument):
    def __init__(self):
        super().__init__("f", "first", "", "Runs first-time setup", MAIN_PRIORITY)


class EraseArgument(Argument):
    def __init__(self):
        super().__init__("e", "erase", "", "Removes tarstall from your system", MAIN_PRIORITY)


class VerboseArgument(Argument):
    def __init__(self):
        super().__init__("v", "verbose", "", "Enables verbose mode for this run of tarstall", 1)


class UpdateTarstallArgument(Argument):
    def __init__(self):
        super().__init__("u", "update", "", "Updates tarstall if an update is available", MAIN_PRIORITY)


class UpdateProgramArgument(ProgramArgument):
    def __init__(self):
        super().__init__("m", "manage", "[PROGRAM]", "Manage the program named [PROGRAM]", MAIN_PRIORITY)


class RemoveLockArgument(Argument):
    def __init__(self):
        super().__init__("k", "remove-lock", "",
                         "Removes tarstall's lock (only do this if tarstall isn't already running)", 3)


class ConfigArgument(Argument):
    def __init__(self):
        super().__init__("c", "config", "", "Configure tarstall", MAIN_PRIORITY)


class UpgradeArgument(Argument):

    def __init__(self):
        super().__init__("q", "update-programs", "[PROGRAM]",
                         "Updates [PROGRAM], or all programs if [PROGRAM] is not specified", MAIN_PRIORITY)
        self.prog_argument = ProgramArgument()

    def arg_count(self, argv):
        if len(argv) == 0:
            return 0
        else:
            return self.prog_argument.arg_count(argv)

    def get_next(self, argv):
        extra = [""] if len(argv) == 0 else []
        return list(self.prog_argument.get_next(argv)) + extra




