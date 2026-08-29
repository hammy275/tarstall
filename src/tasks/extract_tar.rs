use std::{fs};
use std::fs::File;
use std::path::PathBuf;
use flate2::read::GzDecoder;
use tar::Archive;
use crate::task::{ProgressReporter, Task, TaskResult, ToTaskResultExt};
use crate::tasks::extract_tar::ExtractTarMode::{Tar, TarGz};

pub struct ExtractTar {
    pub src: PathBuf,
    pub dst: PathBuf,
    pub mode: ExtractTarMode
}

impl Task for ExtractTar {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        let mode = self.get_actual_mode()?;
        if let Err(err) = fs::create_dir_all(self.dst.clone()) {
            return Err(err.to_string());
        }
        progress_reporter.progress(0.05);
        match File::open(self.src.clone()) {
            Ok(file) => {
                if mode == TarGz {
                    let tar = GzDecoder::new(file);
                    let mut archive = Archive::new(tar);
                    archive.unpack(self.dst.clone()).task_result()
                } else {
                    let mut archive = Archive::new(file);
                    archive.unpack(self.dst.clone()).task_result()
                }
            }
            Err(err) => Err(err.to_string())
        }
    }

    fn undo(&self) -> TaskResult {
        fs::remove_dir_all(self.dst.clone()).task_result()
    }
}

impl ExtractTar {
    fn get_actual_mode(&self) -> Result<ExtractTarMode, String> {
        if let ExtractTarMode::Auto = self.mode {
            let Some(path_str) = self.src.to_str() else {
                return Err("could not determine extraction mode".to_string())
            };
            if path_str.ends_with(".tar.gz") {
                Ok(TarGz)
            } else if path_str.ends_with(".tar") {
                Ok(Tar)
            } else {
                Err("could not determine extraction mode".to_string())
            }
        } else {
            Ok(self.mode)
        }
    }
}

#[derive(Copy, Clone, PartialEq, Eq)]
pub enum ExtractTarMode {
    Tar,
    TarGz,
    Auto
}

#[cfg(test)]
mod tests {
    use std::fs::File;
    use std::path::PathBuf;
    use std::str::FromStr;
    use flate2::Compression;
    use flate2::write::GzEncoder;
    use tar::Builder;
    use crate::task::run_task;
    use crate::tasks::extract_tar::{ExtractTar, ExtractTarMode};
    use crate::tasks::extract_tar::ExtractTarMode::{Auto, Tar, TarGz};
    use crate::util::temp_dir;

    #[test]
    fn test_tar_extraction() {
        do_test_tar_extraction(Tar)
    }

    #[test]
    fn test_tar_extraction_auto() {
        do_test_tar_extraction(Auto)
    }

    fn do_test_tar_extraction(mode: ExtractTarMode) {
        let temp_dir = temp_dir().unwrap();
        let path = temp_dir.path.join("test.tar");
        let file = File::create(path.clone()).unwrap();
        let mut builder = Builder::new(file);
        builder.append_path(PathBuf::from_str("./.gitignore").unwrap()).unwrap();
        builder.into_inner().unwrap();

        let task = ExtractTar{
            src: path,
            dst: temp_dir.path.clone(),
            mode,
        };
        assert!(run_task(&task).is_ok());
    }

    #[test]
    fn test_tar_gz_extraction() {
        do_test_tar_gz_extraction(TarGz)
    }

    #[test]
    fn test_tar_gz_extraction_auto() {
        do_test_tar_gz_extraction(Auto)
    }

    fn do_test_tar_gz_extraction(mode: ExtractTarMode) {
        let temp_dir = temp_dir().unwrap();
        let path = temp_dir.path.join("test.tar.gz");
        let file = File::create(path.clone()).unwrap();
        let file_gz = GzEncoder::new(file, Compression::fast());
        let mut builder = Builder::new(file_gz);
        builder.append_path(PathBuf::from_str("./.gitignore").unwrap()).unwrap();
        builder.into_inner().unwrap();

        let task = ExtractTar{
            src: path,
            dst: temp_dir.path.clone(),
            mode,
        };
        assert!(run_task(&task).is_ok());
    }
}