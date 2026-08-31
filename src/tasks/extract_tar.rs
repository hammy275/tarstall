use std::{fs};
use std::cell::RefCell;
use std::fs::File;
use std::io::Read;
use std::path::PathBuf;
use flate2::read::GzDecoder;
use lzma_rust2::XzReader;
use tar::Archive;
use crate::task::{ProgressReporter, ProgressSender, Task, TaskResult, ToTaskResultExt};
use crate::tasks::extract_tar::ExtractTarMode::{Tar, TarGz, TarXz};

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
                let Ok(metadata) = file.metadata() else {
                    return Err("could not get file metadata".to_string())
                };
                let intercepted_file = ReadProgressInterceptor::new(file, metadata.len(), 0.05, 0.95, progress_reporter.clone());
                match mode {
                    Tar => {
                        let archive = Archive::new(intercepted_file);
                        self.unpack(archive)
                    }
                    TarGz => {
                        let gz = GzDecoder::new(intercepted_file);
                        let archive = Archive::new(gz);
                        self.unpack(archive)
                    }
                    TarXz => {
                        let xz = XzReader::new(intercepted_file, true);
                        let archive = Archive::new(xz);
                        self.unpack(archive)
                    }
                    ExtractTarMode::Auto => panic!("should be unreachable")
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
            } else if path_str.ends_with(".tar.xz") {
                Ok(TarXz)
            } else if path_str.ends_with(".tar") {
                Ok(Tar)
            } else {
                Err("could not determine extraction mode".to_string())
            }
        } else {
            Ok(self.mode)
        }
    }

    fn unpack<T: Read>(&self, mut archive: Archive<T>) -> TaskResult {
        archive.unpack(self.dst.clone()).task_result()
    }
}

/// Intercepts reading something (a file) for progress. This isn't perfectly accurate for a few
/// reasons (listed below), but is more than good enough for a progress bar.
/// - The entire file isn't actually read outside for some cases! That said, almost all of it is,
///   and most of an archive is the files themselves, which definitely need to be read in-full.
/// - Given where this sits, we intercept the reading, but none of the decompression or writing.
///   This is a bit early, but given we don't keep the whole file in memory before writing any
///   of it, this is fine enough.
struct ReadProgressInterceptor<R: Read> {
    /// The thing being read.
    inner: RefCell<R>,
    /// Inner-state of how many bytes have been read so far. Note that f64s are used since we float
    /// divide later on. Of note is that f64 can go up to 2^53 bytes (about 9 PB) before we suffer
    /// from any float precision loss for the whole numbers we're working with.
    bytes_read: f64,
    /// Total size of the thing being read.
    total_size: f64,
    /// Where the start of progress keeping should be.
    start_progress: f64,
    /// The weight of this read. A start_progress of 0.05 and a progress_amount of 0.9 means this
    /// will report up to 0.95.
    progress_amount: f64,
    /// Progress reporter to send progress to.
    progress_reporter: ProgressReporter

}

impl<R: Read> ReadProgressInterceptor<R> {
    /// Create a ReadProgressInterceptor from the thing being read, its size, the start progress
    /// that would be reported when 0% read, the end progress that would be reported when 100% read,
    /// and the progress reporter to send progress to.
    fn new(inner: R, total_size: u64, start_progress: f64, end_progress: f64, progress_reporter: ProgressReporter) -> ReadProgressInterceptor<R> {
        ReadProgressInterceptor {
            inner: RefCell::new(inner),
            bytes_read: 0.0,
            total_size: total_size as f64,
            start_progress,
            progress_amount: end_progress - start_progress,
            progress_reporter
        }
    }
}

impl<R: Read> Read for ReadProgressInterceptor<R> {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        // Do the read.
        let ret = self.inner.borrow_mut().read(buf);
        // Increment bytes_read and report progress if we succeed.
        if let Ok(amount) = ret {
            self.bytes_read += amount as f64;
            let progress = self.bytes_read / self.total_size;
            self.progress_reporter.progress(self.start_progress + progress * self.progress_amount);
        }
        // Return original result.
        ret
    }
}

#[derive(Copy, Clone, PartialEq, Eq)]
pub enum ExtractTarMode {
    Tar,
    TarGz,
    TarXz,
    Auto
}

#[cfg(test)]
mod tests {
    use std::fs::File;
    use std::path::PathBuf;
    use std::str::FromStr;
    use flate2::Compression;
    use flate2::write::GzEncoder;
    use lzma_rust2::{XzOptions, XzWriter};
    use tar::Builder;
    use crate::task::run_task;
    use crate::tasks::extract_tar::{ExtractTar, ExtractTarMode};
    use crate::tasks::extract_tar::ExtractTarMode::{Auto, Tar, TarGz, TarXz};
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
        builder.append_path(PathBuf::from_str("./readme-images/gui.png").unwrap()).unwrap();
        builder.append_path(PathBuf::from_str("./readme-images/terminal.png").unwrap()).unwrap();
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
        builder.append_path(PathBuf::from_str("./readme-images/gui.png").unwrap()).unwrap();
        builder.append_path(PathBuf::from_str("./readme-images/terminal.png").unwrap()).unwrap();
        builder.into_inner().unwrap();

        let task = ExtractTar{
            src: path,
            dst: temp_dir.path.clone(),
            mode,
        };
        assert!(run_task(&task).is_ok());
    }

    #[test]
    fn test_tar_xz_extraction() {
        do_test_tar_xz_extraction(TarXz)
    }

    #[test]
    fn test_tar_xz_extraction_auto() {
        do_test_tar_xz_extraction(Auto)
    }

    fn do_test_tar_xz_extraction(mode: ExtractTarMode) {
        let temp_dir = temp_dir().unwrap();
        let path = temp_dir.path.join("test.tar.xz");
        let file = File::create(path.clone()).unwrap();
        let file_xz = XzWriter::new(file, XzOptions::default()).unwrap().auto_finish();
        let mut builder = Builder::new(file_xz);
        builder.append_path(PathBuf::from_str("./readme-images/gui.png").unwrap()).unwrap();
        builder.append_path(PathBuf::from_str("./readme-images/terminal.png").unwrap()).unwrap();
        builder.into_inner().unwrap();

        let task = ExtractTar{
            src: path,
            dst: temp_dir.path.clone(),
            mode,
        };
        assert!(run_task(&task).is_ok());
    }
}