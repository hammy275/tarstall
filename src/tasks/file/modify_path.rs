use std::env::consts::OS;
use std::path::PathBuf;
use crate::task::{ProgressReporter, Task, TaskResult};

pub struct ModifyPath {
    pub path: PathBuf,
    pub operation: ModifyPathOperation
}

impl Task for ModifyPath {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        match self.operation {
            ModifyPathOperation::Add => self.add_to_path(),
            ModifyPathOperation::Remove => self.remove_from_path()
        }
    }

    fn undo(&self) -> TaskResult {
        match self.operation {
            ModifyPathOperation::Add => self.remove_from_path(),
            ModifyPathOperation::Remove => self.add_to_path()
        }
    }
}

impl ModifyPath {
    fn add_to_path(&self) -> TaskResult {
        if OS == "windows" {
            let mut PATH = read_reg_path()?;
            if !PATH.ends_with(";") {
                PATH += ";";
            }
            let to_add_str = self.get_windows_path_str()?;
            PATH += to_add_str.as_str();
            write_reg_path(PATH.as_str())
        } else {
            todo!("*.nix support")
        }
    }

    fn remove_from_path(&self) -> TaskResult {
        if OS == "windows" {
            let mut PATH = read_reg_path()?;
            if !PATH.ends_with(";") {
                PATH += ";";
            }
            let mut to_remove_str = self.get_windows_path_str()? + ";";
            match PATH.find(&to_remove_str) {
                None => return Err(format!("could not find \"{}\" in PATH", to_remove_str).to_string()),
                Some(start) => PATH.replace_range(start..start + to_remove_str.len(), "")
            };
            write_reg_path(PATH.as_str())
        } else {
            todo!("*.nix support")
        }
    }

    fn get_windows_path_str(&self) -> Result<String, String> {
        let mut to_add_str = match self.path.to_str() {
            None => return Err("cannot convert path to string".to_string()),
            Some(to_add_str) => to_add_str.to_string()
        };
        if to_add_str.contains(";") {
            to_add_str = r"\".to_string() + to_add_str.as_str() + r"\";
        };
        Ok(to_add_str)
    }
}

pub enum ModifyPathOperation {
    Add,
    Remove
}

#[cfg(target_os = "windows")]
fn read_reg_path() -> Result<String, String> {
    use windows_registry::CURRENT_USER;
    match CURRENT_USER.open(r"Environment") {
        Ok(key) => {
            match key.get_string("Path") {
                Ok(val) => Ok(val),
                Err(err) => Err(err.to_string())
            }
        }
        Err(err) => Err(err.to_string())
    }
}

#[cfg(target_os = "windows")]
fn write_reg_path(new_path: &str) -> Result<(), String> {
    use windows_registry::CURRENT_USER;
    match CURRENT_USER.create(r"Environment") {
        Ok(key) => {
            key.set_expand_string("Path", new_path)
                .map_err(| err | { err.to_string() })
        }
        Err(err) => Err(err.to_string())
    }
}

#[cfg(not(target_os = "windows"))]
fn read_reg_path() -> Result<String, String> {
    Err("can only read Registry on Windows".to_string())
}

#[cfg(not(target_os = "windows"))]
fn write_reg_path(new_path: &str) -> Result<(), String> {
    Err("can only write Registry on Windows".to_string())
}

#[cfg(test)]
#[cfg(target_os = "windows")]
mod tests_windows {
    use std::path::PathBuf;
    use crate::task::run_task;
    use crate::tasks::file::modify_path::{read_reg_path, ModifyPath, ModifyPathOperation};

    #[test]
    fn test_add_remove() {
        let mut original = read_reg_path().unwrap();
        if !original.ends_with(";") {
            original += ";"
        }

        let add_task = ModifyPath{
            path: PathBuf::from(r"C:\Test"),
            operation: ModifyPathOperation::Add,
        };
        assert!(run_task(&add_task).is_ok());
        assert!(read_reg_path().unwrap().contains(r"C:\Test"));

        let remove_task = ModifyPath{
            path: PathBuf::from(r"C:\Test"),
            operation: ModifyPathOperation::Remove,
        };
        assert!(run_task(&remove_task).is_ok());
        assert!(!read_reg_path().unwrap().contains(r"C:\Test"));

        assert_eq!(read_reg_path().unwrap(), original);
    }

}