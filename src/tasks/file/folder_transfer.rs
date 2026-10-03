use crate::task::{ProgressReporter, ProgressSender, Task, TaskResult, TaskRunner, Tasks};
use crate::tasks::file::file_transfer::{FileTransfer, TransferMode};
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;


pub struct FolderTransferTask {
    pub source: PathBuf,
    pub destination: PathBuf,
    pub transfer_mode: TransferMode
}

impl Task for FolderTransferTask {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        match create_folder_transfer_tasks(self.source.clone(), self.destination.clone(), self.transfer_mode) {
            None => Err("could not determine files to transfer".to_string()),
            Some(tasks) => {
                let mut task_runner = TaskRunner::create(tasks,
                                                         ProgressSender::Reporter(progress_reporter));
                task_runner.run_tasks()
                    .join()
                    .unwrap_or_else(|_| Err("failed to join child task runner thread".to_string()))
            }
        }
    }

    fn undo(&self) -> TaskResult {
        todo!("Add folder transfer undo")
    }
}

fn create_folder_transfer_tasks(source: PathBuf, destination: PathBuf, transfer_mode: TransferMode) -> Option<Tasks> {
    let mut tasks: Tasks = Vec::new();
    let source_paths = walk(source.clone());
    if let Some(paths) = source_paths {
        for src in paths {
            if let Ok(dst_stripped) = src.strip_prefix(source.clone()) {
                let dst = destination.clone().join(dst_stripped);
                tasks.push((Arc::new(FileTransfer {
                    src,
                    dst,
                    transfer_mode
                }), 1.0))
            } else {
                return None
            }
        }
    } else {
        return None
    }
    Some(tasks)
}


/// Walks the provided file path and returns a vector of all files
fn walk(root: PathBuf) -> Option<Vec<PathBuf>> {
    let mut ret = Vec::new();
    match fs::read_dir(root) {
        Ok(read_dir) => {
            for child in read_dir {
                match child {
                    Ok(dir_entry) => {
                        let path = dir_entry.path();
                        if path.is_dir() {
                            let children = walk(path);
                            match children {
                                Some(mut children) => ret.append(&mut children),
                                None => return None
                            }
                        } else if path.is_file() {
                            ret.push(path);
                        }
                    }
                    Err(_) => return None
                }
            }
        }
        Err(_) => return None
    }
    Some(ret)
}