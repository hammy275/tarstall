from subprocess import Popen, PIPE, STDOUT

import config
from tarstall_error import TarstallHumanReadableError
from task.task import Task, TaskRunner


class WgetTask(Task):
    def __init__(self, url: str):
        self.url = url

    def run(self, task_runner: TaskRunner):
        if config.verbose:
            process = Popen(["wget", self.url])
        else:
            process = Popen(["wget", self.url], stdout=PIPE, stderr=STDOUT)
        if not config.verbose:
            while process.poll() is None:
                p_status = process.stdout.readline().decode("utf-8")
                try:
                    index = p_status.rfind("%")
                    if index != -1:
                        percent_complete = int(p_status[index - 2:index].strip())
                        if percent_complete > 0:
                            task_runner.progress(percent_complete / 100)
                except (TypeError, ValueError):
                    pass
        else:
            process.wait()
        exit_code = process.poll()
        if exit_code != 0:
            raise TarstallHumanReadableError(f"wget exited with non-zero exit code {exit_code}")
        return process.poll()