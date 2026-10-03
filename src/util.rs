use std::{env, fs};
use std::path::PathBuf;
use std::sync::{mpsc, Arc};
use std::time::{SystemTime};
use crate::task::{ProgressSender, Task, TaskRunner, Tasks};
use crate::tasks::file::delete_dir::DeleteDirTask;
use crate::ui::UI;

pub fn wait_for_tasks(tasks: Tasks, ui: &mut dyn UI) -> Result<(), String> {
    let (sender, receiver) = mpsc::channel();
    let mut task_runner = TaskRunner::create(tasks, ProgressSender::Sender(sender));
    let handle = task_runner.run_tasks();
    // TODO: Handle the error case (progress won't hit 1.0 if a task errors out)
    loop {
        match receiver.recv() {
            Ok(progress) => {
                ui.progress(progress);
                if progress == 1.0 {
                    break
                }
            },
            Err(_) => break
        }
    }
    match handle.join() {
        Ok(result) => result,
        Err(_) => Err("task thread panicked".to_string())
    }
}

pub fn home_dir() -> PathBuf {
    // tarstall assumes you have a home directory
    env::home_dir().unwrap_or_else(|| {
        panic!("tarstall cannot be run on a system without a home directory")
    })
}

/// Get a temporary directory that will remove itself when dropped.
pub fn temp_dir() -> Result<TempDir, String> {
    get_temp_dir(true)
}

/// Get a temporary directory that must be manually cleaned up.
pub fn temp_dir_no_autodrop() -> Result<TempDir, String> {
    get_temp_dir(false)
}

fn get_temp_dir(auto_drop: bool) -> Result<TempDir, String> {
    let tmp_root = env::temp_dir().join("tarstall");
    if let Ok(diff) = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        let maybe_subdir = diff.as_nanos().to_string();
        let path = tmp_root.join(maybe_subdir);
        return match fs::create_dir_all(path.clone()) {
            Ok(_) => Ok(TempDir{path, auto_drop}),
            Err(err) => Err(err.to_string())
        }
    }
    Err("cannot make temporary directory on system with time before Jan. 1 1970".to_string())
}

pub struct TempDir {
    pub path: PathBuf,
    auto_drop: bool
}

impl Drop for TempDir {
    fn drop(&mut self) {
        if self.auto_drop {
            // Just a temporary directory, so okay if this fails
            _ = fs::remove_dir_all(self.path.clone())
        }
    }
}

impl TempDir {
    /// Get a task for dropping this temporary directory.
    pub fn get_drop_task(&self) -> Arc<dyn Task> {
        Arc::new(DeleteDirTask{
            path: self.path.clone(),
        })
    }
}