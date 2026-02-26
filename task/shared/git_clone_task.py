from subprocess import call, Popen, STDOUT, PIPE
from typing import Union

import config
from task.task import Task, TaskRunner


class GitCloneTask(Task):
    def __init__(self, url: str, branch: Union[str, None]):
        self.url = url
        self.branch = branch

    def run(self, task_runner: TaskRunner):
        command = ["git", "clone"]
        if self.branch is not None:
            command.append("--branch")
            command.append(self.branch)
        command.append(self.url)
        if config.verbose:
            err = call(command)
        else:
            command.append("--progress")
            process = Popen(command, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
            while process.poll() is None:
                p_status = process.stdout.readline()
                try:
                    percent_complete = int(p_status[p_status.rfind("%") - 2:p_status.rfind("%")].strip())
                    if percent_complete > 0:
                        if "Resolving deltas:" in p_status:
                            task_runner.progress(0.75 + (percent_complete / 100 * 0.25))
                        elif "Receiving objects:" in p_status:
                            task_runner.progress(percent_complete / 100 * 0.75)
                        elif "Unpacking objects:" in p_status:
                            task_runner.progress(percent_complete / 100)
                except (TypeError, ValueError):
                    pass
            err = process.poll()
        return err