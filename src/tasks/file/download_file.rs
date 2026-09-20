use std::fs;
use std::fs::File;
use std::io::{Read, Write};
use std::path::PathBuf;
use crate::task::{ProgressReporter, Task, TaskResult, ToTaskResultExt};

pub struct DownloadFileTask {
    pub url: String,
    pub dst: PathBuf
}

impl Task for DownloadFileTask {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        let mut resp = match reqwest::blocking::get(self.url.as_str()) {
            Ok(resp) => resp,
            Err(err) => return Err(err.to_string())
        };
        let mut file = match File::create_new(self.dst.as_path()) {
            Ok(file) => file,
            Err(err) => return Err(err.to_string())
        };
        match resp.content_length() {
            Some(size) => {
                let total_size: f64 = size as f64;
                let mut size_so_far = 0;
                let mut buffer = [0; 16_384];
                loop {
                    match resp.read(&mut buffer) {
                        Ok(amount_read) => {
                            match amount_read {
                                0 => break,
                                _ => {
                                    match file.write_all(&buffer[0..amount_read]) {
                                        Ok(_) => {
                                            size_so_far += amount_read;
                                            progress_reporter.progress(size_so_far as f64 / total_size);
                                        }
                                        Err(err) => return Err(err.to_string())
                                    }
                                }
                            };
                        }
                        Err(err) => return Err(err.to_string())
                    };
                }

                Ok(())
            },
            None => std::io::copy(&mut resp, &mut file).task_result()
        }
    }

    fn undo(&self) -> TaskResult {
        fs::remove_file(self.dst.as_path()).task_result()
    }
}

#[cfg(test)]
mod tests {
    use crate::task::run_task;
    use crate::tasks::file::download_file::DownloadFileTask;
    use crate::util::temp_dir;

    #[test]
    fn test_download_file_no_progress() {
        let tmp = temp_dir().unwrap();
        let dst = tmp.path.join("file.zip");
        let task = DownloadFileTask{
            url: "https://github.com/hammy275/tarstall/archive/refs/tags/v1.8.0.zip".to_string(),
            dst,
        };
        assert!(run_task(&task).is_ok())
    }

    #[test]
    fn test_download_file_with_progress() {
        let tmp = temp_dir().unwrap();
        let dst = tmp.path.join("file.zip");
        let task = DownloadFileTask{
            url: "https://github.com/hammy275/immersive-mc/releases/download/v1.6.0-alpha4.1/immersivemc-1.6.0-alpha4.1-1.18.2-fabric.jar".to_string(),
            dst,
        };
        assert!(run_task(&task).is_ok())
    }
}