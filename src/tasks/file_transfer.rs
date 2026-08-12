use std::fs;
use std::path::{PathBuf};
use crate::task::{Task, TaskResult, TaskRunner};

/// Task to copy or move a singular file.
pub struct TransferFile {
    src: PathBuf,
    dst: PathBuf,
    transfer_mode: TransferMode
}

impl Task for TransferFile {
    fn run(&self, task_runner: &mut TaskRunner) -> crate::task::TaskResult {
        task_runner.progress(0.1);
        if let Some(parent_path) = self.dst.parent() {
            let result = fs::create_dir_all(parent_path);
            if let Err(_) = result {
                return result.into()
            }
        }
        let result = match self.transfer_mode {
            TransferMode::COPY => fs::copy(&self.src, &self.dst).into(),
            TransferMode::MOVE => fs::rename(&self.src, &self.dst).into()
        };
        task_runner.progress(1.0);
        result
    }

    fn undo(&self, task_runner: &mut TaskRunner) -> crate::task::TaskResult {
        match self.transfer_mode {
            TransferMode::COPY => fs::remove_file(&self.dst).into(),
            TransferMode::MOVE => {
                match fs::exists(&self.dst) {
                    // If destination exists, move it back
                    Ok(true) => fs::rename(&self.dst, &self.src).into(),
                    // If destination doesn't exist, handle based on the source file
                    Ok(false) => {
                        match fs::exists(&self.src) {
                            Ok(true) => TaskResult::Ok,
                            Ok(false) => TaskResult::Err("source and destination files are missing".into()),
                            result @ Err(_) => result.into()
                        }
                    }
                    result @ Err(_) => result.into()
                }
            }
        }
    }
}

enum TransferMode {
    COPY,
    MOVE
}