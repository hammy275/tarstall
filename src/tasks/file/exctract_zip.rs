use crate::task::{ProgressReporter, Task, TaskResult, ToTaskResultExt};
use std::fs::File;
use std::path::PathBuf;
use std::{fs, io};
use zip::ZipArchive;

pub struct ExtractZip {
    pub src: PathBuf,
    pub dst: PathBuf
}

impl Task for ExtractZip {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        let file = match File::open(self.src.clone()) {
            Ok(file) => file,
            Err(err) => return Err(err.to_string())
        };
        let mut archive = match ZipArchive::new(file) {
            Ok(archive) => archive,
            Err(err) => return Err(err.to_string())
        };
        let len = archive.len();
        for i in 0..len {
            let mut file = match archive.by_index(i) {
                Ok(file) => file,
                Err(err) => return Err(err.to_string())
            };
            let out_end_path = match file.enclosed_name() {
                Some(path) => path,
                None => return Err("invalid ZIP (no path for file)".to_string())
            };
            let out_path = self.dst.clone().join(out_end_path);
            if file.is_dir() {
                if let Err(err) = fs::create_dir_all(&out_path) {
                    return Err(err.to_string())
                }
            } else {
                let parent_dir = match out_path.parent() {
                    Some(parent_dir) => parent_dir,
                    None => return Err("no parent directory for ZIP extraction".to_string())
                };
                if let Err(err) = fs::create_dir_all(parent_dir) {
                    return Err(err.to_string())
                }
                let mut out_file = match File::create(&out_path) {
                    Ok(out_file) => out_file,
                    Err(err) => return Err(err.to_string())
                };
                if let Err(err) = io::copy(&mut file, &mut out_file) {
                    return Err(err.to_string());
                }

                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;

                    if let Some(mode) = file.unix_mode() {
                        if let Err(err) = fs::set_permissions(&out_path, Permissions::from_mode(mode)) {
                            return Err(err.to_string())
                        }
                    }
                }
            }
            progress_reporter.progress((i + 1) as f64 / len as f64)
        }
        Ok(())
    }

    fn undo(&self) -> TaskResult {
        fs::remove_dir_all(self.dst.clone()).task_result()
    }
}

#[cfg(test)]
mod tests {
    use crate::task::run_task;
    use crate::tasks::file::exctract_zip::ExtractZip;
    use std::path::PathBuf;

    #[test]
    fn test_extract_zip() {
        let temp_dir = crate::util::temp_dir().unwrap();

        let task = ExtractZip{
            src: PathBuf::from("test/sample_zip.zip").canonicalize().unwrap(),
            dst: temp_dir.path.clone(),
        };
        assert!(run_task(&task).is_ok())
    }
}