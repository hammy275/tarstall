use std::rc::Rc;
use crate::task::{ProgressConsumer, TaskResult, TaskRunner, Tasks};
use crate::tasks::file_transfer::{TransferFile, TransferMode};

mod program;
mod task;
mod tasks;

fn main() {
    let task1 = TransferFile{
        src: "tarstall.exe".parse().unwrap(),
        dst: "tarstall.exe2".parse().unwrap(),
        transfer_mode: TransferMode::COPY
    };
    let task2 = TransferFile{
        src: "tarstall.exe".parse().unwrap(),
        dst: "tarstall.exe3".parse().unwrap(),
        transfer_mode: TransferMode::COPY
    };
    let mut tasks: Tasks = Vec::new();
    tasks.push((Rc::new(task1), 0.5));
    tasks.push((Rc::new(task2), 0.5));
    let progress_consumer = BasicProgressConsumer{};
    let mut task_runner = TaskRunner::create(tasks, Box::new(progress_consumer));
    match task_runner.run_tasks() {
        TaskResult::Ok => println!("Ok"),
        TaskResult::Err(msg) => println!("Error: {}", msg)
    }
}

struct BasicProgressConsumer {}

impl ProgressConsumer for BasicProgressConsumer {
    fn consume_progress(&self, task_runner: &TaskRunner, progress: f64) {
        println!("Progress: {}", progress)
    }
}
