use std::fs;
use std::path::{PathBuf};
use crate::task::{ProgressReporter, Task, TaskResult, TaskRunner};

/// Task to copy or move a singular file.
pub struct FileTransfer {
    pub src: PathBuf,
    pub dst: PathBuf,
    pub transfer_mode: TransferMode
}

impl Task for FileTransfer {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        if let Some(parent_path) = self.dst.parent() {
            let result = fs::create_dir_all(parent_path);
            if let Err(_) = result {
                return result.into()
            }
        }
        progress_reporter.progress(0.1);
        let result = match self.transfer_mode {
            TransferMode::COPY => fs::copy(&self.src, &self.dst).into(),
            TransferMode::MOVE => fs::rename(&self.src, &self.dst).into()
        };
        progress_reporter.progress(1.0);
        result
    }

    fn undo(&self) -> TaskResult {
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

#[derive(Copy, Clone)]
pub enum TransferMode {
    COPY,
    MOVE
}