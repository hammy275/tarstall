use std::sync::Arc;
use std::sync::mpsc::Sender;
use std::thread;
use std::thread::JoinHandle;

/// A type alias for a tuple containing a task and its weight.
pub type TaskWithWeight = (Arc<dyn Task>, f64);
/// A type alias for the list of tasks.
pub type Tasks = Vec<TaskWithWeight>;

/// Something that runs one or more tasks, keeping active progress as it progresses.
pub struct TaskRunner {
    tasks: Tasks,
    progress_sender: ProgressSender
}

impl TaskRunner {

    /// Run the tasks contained within the task runner. These run on a separate thread
    pub fn run_tasks(&mut self) -> JoinHandle<TaskResult> {
        self.normalize_task_weights();
        let tasks = self.tasks.clone();
        let mut progress_reporter = ProgressReporter{
            prev_task_progress: 0.0,
            current_weight: 0.0,
            sender: Box::new(self.progress_sender.clone()),
        };
        thread::spawn(move || {
            for (task, weight) in tasks {
                progress_reporter.current_weight = weight;
                let result: TaskResult = task.run(progress_reporter.clone());
                match result {
                    TaskResult::Ok => {
                        progress_reporter.prev_task_progress += weight
                    },
                    TaskResult::Err(_) => {
                        todo!("Perform rollback");
                        return result
                    }
                }
            }
            TaskResult::Ok
        })
    }

    fn normalize_task_weights(&mut self) {
        let total: f64 = self.tasks.iter()
            .map(| task_and_weight | { task_and_weight.1 })
            .sum();
        for task in self.tasks.iter_mut() {
            (*task).1 = (*task).1 / total
        }
    }

    pub fn create(tasks: Tasks, progress_sender: ProgressSender) -> TaskRunner {
        TaskRunner {
            tasks,
            progress_sender,
        }
    }
}

#[derive(Clone)]
pub struct ProgressReporter {
    prev_task_progress: f64,
    current_weight: f64,
    sender: Box<ProgressSender>
}

impl ProgressReporter {
    pub fn progress(&self, progress: f64) {
        let amount = self.prev_task_progress + self.current_weight * progress;
        match self.sender.as_ref() {
            ProgressSender::Sender(sender) => _ = sender.send(amount),
            ProgressSender::Reporter(progress_reporter) => progress_reporter.progress(amount)
        }
    }

    pub fn create(sender: Box<ProgressSender>) -> ProgressReporter {
        ProgressReporter {
            prev_task_progress: 0.0,
            current_weight: 0.0,
            sender,
        }
    }
}

/// Something that sends progress.
#[derive(Clone)]
pub enum ProgressSender {
    /// A sender that passes along the final value to a receiver.
    Sender(Sender<f64>),
    /// Another ProgressReporter, allowing for chaining multiple ProgressReporters together.
    Reporter(ProgressReporter)
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
pub trait Task: Send + Sync {
    /// Called when the task is run. Progress should be reported via the provided ProgressReporter.
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult;
    /// Called when the task fails, and it should undo any changes it made (if any). One should
    /// especially expect this to be called if run() returns an Error.
    fn undo(&self) -> TaskResult;
}