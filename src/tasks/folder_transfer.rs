use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use crate::task::Tasks;
use crate::tasks::file_transfer::{TransferFile, TransferMode};
use crate::tasks::task_of_tasks::TaskOfTasks;

pub fn create_folder_transfer(source: PathBuf, destination: PathBuf, transfer_mode: TransferMode) -> Option<TaskOfTasks> {
    let mut tasks: Tasks = Vec::new();
    let source_paths = walk(source.clone());
    if let Some(paths) = source_paths {
        for src in paths {
            if let Ok(dst_stripped) = src.strip_prefix(source.clone()) {
                let dst = destination.clone().join(dst_stripped);
                tasks.push((Arc::new(TransferFile{
                    src,
                    dst,
                    transfer_mode
                }), 1.0))
            }
        }
    }
    Some(TaskOfTasks{ tasks })

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