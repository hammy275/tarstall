from subprocess import Popen, PIPE, STDOUT, call, DEVNULL

import config
import generic

try:
    import requests
    can_update = True
except ImportError:
    can_update = False

if config.verbose:
    c_out = None
else:
    c_out = DEVNULL


def wget_with_progress(url, start_percent, end_percent, show_progress=True):
    """Wget with Progress.

    The wget version of git_clone_with_progress()

    Args:
        url (str): URL to file to grab
        start_percent (int): Where generic.progress() last was
        end_percent (int): Where generic.progress() should end up
        show_progress (bool, optional): Whether to show progress if not verbose. Defaults to True.

    Returns:
        int: Exit code from wget

    """
    if config.verbose:
        process = Popen(["wget", url])
    else:
        process = Popen(["wget", url], stdout=PIPE, stderr=STDOUT)
    if not config.verbose and show_progress:
        while process.poll() is None:
            p_status = process.stdout.readline().decode("utf-8")
            try:
                index = p_status.rfind("%")
                if index != -1:
                    percent_complete = int(p_status[index-2:index].strip())
                    if percent_complete > 0:
                        generic.progress(start_percent + ((end_percent - start_percent) * (percent_complete / 100)))
            except (TypeError, ValueError):
                pass
    else:
        process.wait()
    return process.poll()


def git_clone_with_progress(url, start_percent, end_percent, branch=None):
    """Performs a Git Clone with Progress.

    Args:
        url (str): URL to git clone from
        start_percent (int): Starting value for generic.progress()
        end_percent (int): Ending value for generic.progress()
        branch (str): If specified, use a custom branch to clone from. Defaults to None.

    Returns:
        [int: Exit code from git
    """
    command = ["git", "clone"]
    if branch is not None:
        command.append("--branch")
        command.append(branch)
    command.append(url)
    if config.verbose:
        err = call(command)
    else:
        command.append("--progress")
        process = Popen(command, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
        multiplier = end_percent - start_percent
        while process.poll() is None:
            p_status = process.stdout.readline()
            try:
                percent_complete = int(p_status[p_status.rfind("%")-2:p_status.rfind("%")].strip())
                if percent_complete > 0:
                    if "Resolving deltas:" in p_status:
                        generic.progress(start_percent + int(multiplier * 0.6) + (int(multiplier * 0.4) * (percent_complete / 100)))
                    elif "Receiving objects:" in p_status:
                        generic.progress(start_percent + (int(multiplier * 0.6) * (percent_complete / 100)))
                    elif "Unpacking objects:" in p_status:
                        generic.progress(start_percent + (multiplier * (percent_complete / 100)))
            except (TypeError, ValueError):
                    pass
        err = process.poll()
    return err