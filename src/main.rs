use std::sync::Arc;
use std::sync::mpsc::channel;
use crate::task::{TaskResult, TaskRunner, Tasks};
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
    tasks.push((Arc::new(task1), 0.5));
    tasks.push((Arc::new(task2), 0.5));
    let (sender, receiver) = channel();
    let mut task_runner = TaskRunner::create(tasks, sender);
    let run_tasks_handle = task_runner.run_tasks();
    let mut progress = 0.0;
    while (progress < 1.0) {
        match receiver.recv() {
            Result::Ok(amount) => {
                progress = amount;
                println!("Progress: {}", progress)
            }
            _ => break
        }
    }
    match run_tasks_handle.join() {
        Result::Ok(task_result) => {
            match task_result {
                TaskResult::Ok => println!("Done!"),
                TaskResult::Err(msg) => println!("Error: {}", msg)
            }
        }
        Result::Err(err) => println!("Join error")
    }

}
