use std::rc::Rc;

/// A basic type containing a task and its weight.
type TaskWithWeight = (Rc<dyn Task>, f64);

/// Something that runs one or more tasks, keeping active progress as it progresses.
pub struct TaskRunner {
    prev_task_progress: f64,
    tasks: Vec<TaskWithWeight>,
    current_weight: f64,
    progress_consumer: dyn FnMut(f64)
}

impl TaskRunner {

    /// Update the progress for the task runner. Should only be called from within a task.
    pub fn progress(&mut self, amount: f64) {
        match amount {
            0.0..1.0 => {
                let new_progress = self.prev_task_progress + self.current_weight * amount;
                (self.progress_consumer)(new_progress)
            }
            _ => panic!("Progress should be in the range [0.0, 1.0]")
        }
    }

    /// Run the tasks contained within the task runner.
    pub fn run_tasks(&mut self) -> TaskResult {
        self.normalize_task_weights();
        let tasks = self.tasks.clone();
        for (task, weight) in tasks {
            self.current_weight = weight;
            let result: TaskResult = task.run(self);
            match result {
                TaskResult::Ok => {
                    self.prev_task_progress += self.current_weight
                },
                TaskResult::Err(_) => {
                    todo!("Perform rollback");
                    return result
                }
            }
        }
        TaskResult::Ok
    }

    fn normalize_task_weights(&mut self) {
        let total: f64 = self.tasks.iter()
            .map(| task_and_weight | { task_and_weight.1 })
            .sum();
        for task in self.tasks.iter_mut() {
            (*task).1 = (*task).1 / total
        }
    }
}

/// The result of a task. Either a success (returning unit) or an error message.
/// Doesn't use the pre-existing Result to avoid the .0 pattern from newtypes and to still allow
/// implementing traits on it.
pub enum TaskResult {
    Ok,
    Err(String)
}

impl<T> From<std::io::Result<T>> for TaskResult {
    fn from(io_result: std::io::Result<T>) -> Self {
        match io_result {
            Ok(_) => TaskResult::Ok,
            Err(error) => TaskResult::Err(error.to_string())
        }
    }
}

/// A task that performs some operation, marking progress using the provided task runner, then
/// returns a success or failure.
pub trait Task {
    /// Called when the task is run. Progress should be reported via the task_runner's progress()
    /// method.
    fn run(&self, task_runner: &mut TaskRunner) -> TaskResult;
    /// Called when the task fails, and it should undo any changes it made (if any). Progress for
    /// this should not be reported to the task_runner. One should especially expect this to be
    /// called if run() returns an Error.
    fn undo(&self, task_runner: &mut TaskRunner) -> TaskResult;
}