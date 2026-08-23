use std::{env, fs, io};
use std::path::PathBuf;
use std::time::{SystemTime};

pub fn get_temp_dir() -> Result<TempDir, String> {
    let tmp_root = env::temp_dir().join("tarstall");
    if let Ok(diff) = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        let maybe_subdir = diff.as_nanos().to_string();
        let path = tmp_root.join(maybe_subdir);
        return match fs::create_dir_all(path.clone()) {
            Ok(_) => Ok(TempDir{path}),
            Err(err) => Err(err.to_string())
        }
    }
    Err("cannot make temporary directory on system with time before Jan. 1 1970".to_string())
}

pub struct TempDir {
    pub path: PathBuf
}

impl Drop for TempDir {
    fn drop(&mut self) {
        // Just a temporary directory, so okay if this fails
        _ = fs::remove_dir_all(self.path.clone())
    }
}