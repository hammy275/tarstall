from __future__ import annotations  # For forward declaring type-hints (they internally become strings)
from abc import ABC, abstractmethod
from typing import Callable

import config
import generic


class TaskRunner:
    """Task runner.

    Task runner that runs tasks.

    Args:
        tasks list[tuple[Task, float]]: A list of tasks and the weight they should have for progress. Weights should
                                        always add up to 1.0.
        progress_consumer Callable[[float, bool], None]: A function to call for updating the progress. Passed the
                                                         actual progress in the range [0, 1.0] and a bool of whether
                                                         to show it.
    """
    def __init__(self, tasks: list[tuple[Task, float]], progress_consumer: Callable[[float, bool], None]):
        self.tasks = tasks
        self.progress_consumer = progress_consumer

        self.base_progress = 0  # Progress from all past tasks
        self.current_task_weight = 0  # Weight for the current task

    def run_tasks(self):
        """Run all tasks.

        Run all tasks provided to the task runner.
        """
        for task, weight in self.tasks:
            self.current_task_weight = weight
            task.run(self)
            self.base_progress += weight

    def progress(self, amount: float):
        """Update progress for tasks.

        Called by tasks to update progress.

        Args:
            amount (float): An amount in the range [0.0, 1.0] of how close to complete the task is.
        """
        new_progress = self.base_progress + amount * self.current_task_weight
        self.progress_consumer(new_progress, not config.verbose)


def display_task_runner(tasks: list[tuple[Task, float]]) -> TaskRunner:
    """Create a task runner for direct display.

    Creates a task runner where progress is directly outputted to the progress bar shown to the user.

    Args:
        tasks list[tuple[Task, float]]: A list of tasks and the weight they should have for progress. Weights should
                                always add up to 1.0.

    Returns:
        A task runner as described.
    """
    return TaskRunner(tasks, lambda amount, show_progress: generic.progress(amount * 100, show_progress))


def sub_task_runner(tasks: list[tuple[Task, float]], parent: TaskRunner) -> TaskRunner:
    """Create a task runner as a child of another task runner.

    Creates a task runner where progress is passed to a parent task runner. Should only be used within tasks already
    running on the parent task runner.

    Args:
        tasks list[tuple[Task, float]]: A list of tasks and the weight they should have for progress. Weights should
                                always add up to 1.0.

    Returns:
        A task runner as described.
    """
    return TaskRunner(tasks, lambda amount, ignored: parent.progress(amount))


class Task(ABC):
    """Task.

    Task that is run by TaskRunner. Should be extended to create different implementations.
    """
    @abstractmethod
    def run(self, task_runner: TaskRunner):
        """Run task.

        Runs this task. Tasks are only required to be runnable once. They can raise any error to denote a failure,
        or should simply not do so on a success.

        Args:
            task_runner (TaskRunner): The task runner running the task.
        """
        pass