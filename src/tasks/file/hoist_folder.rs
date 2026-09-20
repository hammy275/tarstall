use std::fs;
use std::path::{PathBuf};
use crate::task::{ProgressReporter, Task, TaskResult};
use crate::util::temp_dir;

/// Task that repeatedly hoists the contents of a folder up if the contents are themselves one
/// folder.
pub struct HoistFolder {
    pub target: PathBuf
}

impl Task for HoistFolder {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        loop {
            let read_dir = fs::read_dir(&self.target).map_err(| err | { err.to_string() })?;
            let mut folder_to_hoist = None;
            let mut found_something = false;
            for folder_res in read_dir {
                if found_something {
                    return Ok(())
                }
                found_something = true;
                let folder = folder_res.map_err(| err | { err.to_string() })?;
                if folder.path().is_dir() {
                    folder_to_hoist = Some(folder)
                }
            }
            match folder_to_hoist {
                None => return Ok(()),
                Some(src_entry) => {
                    let src = src_entry.path();
                    let temp = temp_dir()?;
                    let mid = &temp.path;
                    let dst = match src.parent() {
                        None => return Err("could not get parent directory for hoisting folder".to_string()),
                        Some(dst) => dst
                    };
                    if let Err(err) = fs::rename(&src, mid) {
                        return Err(err.to_string())
                    }
                    if let Err(err) = fs::rename(mid, dst) {
                        return Err(err.to_string())
                    }
                }
            }
        }
    }

    fn undo(&self) -> TaskResult {
        // Intentional no-op: No tarstall context necessitates that this undo work (since this
        // happens at the end of installation, where the folder will just get nuked during undo
        // anyway).
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use std::fs;
    use std::fs::File;
    use std::io::Write;
    use crate::task::run_task;
    use crate::tasks::file::hoist_folder::HoistFolder;
    use crate::util::temp_dir;

    #[test]
    fn test_hoist_empty() {
        let temp = temp_dir().unwrap();
        _ = fs::create_dir_all(temp.path.join("a").join("b").join("c")).unwrap();
        let task = HoistFolder{
            target: temp.path.clone()
        };
        assert!(run_task(&task).is_ok());
        assert!(temp.path.is_dir());
        assert!(fs::read_dir(&temp.path).unwrap().next().is_none());
    }

    #[test]
    fn test_hoist_not_empty() {
        let temp = temp_dir().unwrap();
        let nested_path = temp.path.join("a").join("b").join("c");
        _ = fs::create_dir_all(&nested_path).unwrap();
        _ = File::create(nested_path.join("test.txt")).unwrap();
        let task = HoistFolder{
            target: temp.path.clone()
        };
        assert!(run_task(&task).is_ok());
        assert!(temp.path.is_dir());
        assert!(temp.path.join("test.txt").is_file());
    }
}