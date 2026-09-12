use crate::args::InstallArgs;
use crate::config::{has_program, tarstall_home};
use crate::exec::install::InstallSource::{File, Folder, Git, Url};
use crate::program::InstallType::DEFAULT;
use crate::task::{Task, TaskResult, TaskWithWeight, Tasks};
use crate::tasks::db::add_program::AddProgram;
use crate::tasks::file::exctract_zip::ExtractZip;
use crate::tasks::file::extract_tar::{ExtractTar, ExtractTarMode};
use crate::tasks::file::file_transfer::TransferMode;
use crate::tasks::file::folder_transfer::create_folder_transfer;
use crate::ui::UI;
use crate::util::wait_for_tasks;
use std::path::PathBuf;
use std::sync::Arc;

pub fn install(args: &InstallArgs, ui: &mut dyn UI) -> TaskResult {
    let source = parse_source(args.source.clone())?;
    let name = match &args.name {
        None => get_name(&source).ok_or("Name could not be automatically determined, please provide a name for this program".to_string())?,
        Some(name) => name.clone()
    };
    if has_program(name.as_str()) {
        return Err(format!("{} is already installed!", name))
    }
    let dst = tarstall_home().join("bin").join(name.clone());
    let mut tasks: Tasks = Vec::new();
    match source {
        Url(_) => todo!("url install unimplemented"),
        File(ref file_path) => tasks.push(get_file_extract_task(file_path, &dst)),
        Folder(ref folder_path) => match create_folder_transfer(folder_path.to_path_buf(), dst.clone(), TransferMode::COPY) {
            Some(folder_transfer) => tasks.push((Arc::new(folder_transfer), 100.0)),
            None => return Err("failed to get directories for copying".to_string())
        }
        Git(_) => todo!("git install unimplemented"),
    }
    tasks.push((Arc::new(AddProgram{
        name,
        install_type: match source {
            Url(_) => todo!("url install unimplemented"),
            // Both unwraps here are safe as they are in get_file_extract_task()
            File(ref file_path) => DEFAULT {update_archive_type: Some(file_path.extension().unwrap().to_str().unwrap().to_string())},
            Folder(_) => DEFAULT {update_archive_type: None},
            Git(_) => todo!("git install unimplemented")
        },
        update_url: None,
    }), 1.0));
    wait_for_tasks(tasks, ui)
}

fn get_file_extract_task(file_path: &PathBuf, dst: &PathBuf) -> TaskWithWeight {
    // First unwrap safe since File() means there is a file extension already.
    // Second unwrap safe since it came from a string earlier anyway
    let extension = file_path.extension().unwrap().to_str().unwrap();
    if extension.to_lowercase() == "zip" {
        (Arc::new(ExtractZip{
            src: file_path.to_path_buf(),
            dst: dst.clone(),
        }), 1.0)
    } else {
        (Arc::new(ExtractTar{
            src: file_path.to_path_buf(),
            dst: dst.clone(),
            mode: ExtractTarMode::Auto,
        }), 1.0)
    }
}

fn parse_source(source: String) -> Result<InstallSource, String> {
    if source.starts_with("http://") || source.starts_with("https://") {
        if source.ends_with(".git") {
            Ok(Git(source))
        } else {
            Ok(Url(source))
        }
    } else {
        let path = PathBuf::from(source);
        if path.is_file() {
            Ok(File(path.canonicalize().map_err(| err | { "could not get path to file" })?))
        } else if path.is_dir() {
            Ok(Folder(path.canonicalize().map_err(| err | { "could not get path to folder" })?))
        } else {
            // Safe to unwrap since it came from a string earlier
            Err(format!("{} not found", path.to_str().unwrap()))
        }
    }
}

fn get_name(source: &InstallSource) -> Option<String> {
    match source {
        // Get everything between the last / and the first .
        Url(url) | Git(url) => url.split("/").last()
            .map(| end_of_path | {
                match end_of_path.split_once(".") {
                    None => end_of_path.to_string(),
                    Some(split) => split.0.to_string()
                }
            }),
        // Get last part of path, then everything before the first .
        File(path) => path.iter().last()
            .and_then(| os_str | { os_str.to_str() } )
            .map(| str | { str.to_string() })
            .map(| str | {
                match str.split_once(".") {
                    None => str,
                    Some(split) => split.0.to_string()
                }
            }),
        // Just get the last part of path
        Folder(path) => path.iter().last()
            .and_then(| os_str | { os_str.to_str() } )
            .map(| str | { str.to_string() })
    }
}

#[derive(Clone, PartialEq, Eq, Debug)]
enum InstallSource {
    Url(String),
    File(PathBuf),
    Folder(PathBuf),
    Git(String)
}

#[cfg(test)]
mod tests {
    use crate::exec::install::InstallSource::{File, Folder, Git, Url};
    use crate::exec::install::{get_name, parse_source};
    use std::path::PathBuf;

    #[test]
    fn test_parse_url() {
        let res = parse_source("http://example.com/file.tar.gz".to_string());
        assert_eq!(res.unwrap(), Url("http://example.com/file.tar.gz".to_string()));
        let res = parse_source("https://example.com/file.tar.gz".to_string());
        assert_eq!(res.unwrap(), Url("https://example.com/file.tar.gz".to_string()));
    }

    #[test]
    fn test_get_name_url() {
        let res = get_name(&Url("http://example.com/file.tar.gz".to_string()));
        assert_eq!(res.unwrap(), "file".to_string());
        let res = get_name(&Url("https://example.com/file.tar.gz".to_string()));
        assert_eq!(res.unwrap(), "file".to_string());
    }

    #[test]
    fn test_parse_git() {
        let res = parse_source("http://example.com/repo.git".to_string());
        assert_eq!(res.unwrap(), Git("http://example.com/repo.git".to_string()));
        let res = parse_source("https://example.com/repo.git".to_string());
        assert_eq!(res.unwrap(), Git("https://example.com/repo.git".to_string()));
    }

    #[test]
    fn test_get_name_git() {
        let res = get_name(&Git("http://example.com/repo.git".to_string()));
        assert_eq!(res.unwrap(), "repo".to_string());
        let res = get_name(&Git("https://example.com/repo.git".to_string()));
        assert_eq!(res.unwrap(), "repo".to_string());
    }

    #[test]
    fn test_parse_file() {
        let res = parse_source("./Cargo.toml".to_string());
        assert_eq!(res.clone().unwrap(), File(PathBuf::from("../../Cargo.toml").canonicalize().unwrap()));
        let res2 = parse_source("Cargo.toml".to_string());
        assert_eq!(res2.clone().unwrap(), File(PathBuf::from("../../Cargo.toml").canonicalize().unwrap()));
        assert_eq!(res.unwrap(), res2.unwrap());
    }

    #[test]
    fn test_get_name_file() {
        let res = get_name(&File(PathBuf::from("../../Cargo.toml")));
        assert_eq!(res.unwrap(), "Cargo".to_string());
    }

    #[test]
    fn test_parse_folder() {
        let res = parse_source("./src".to_string());
        assert_eq!(res.clone().unwrap(), Folder(PathBuf::from("..").canonicalize().unwrap()));
        let res2 = parse_source("src".to_string());
        assert_eq!(res2.clone().unwrap(), Folder(PathBuf::from("..").canonicalize().unwrap()));
        assert_eq!(res.unwrap(), res2.unwrap())
    }

    #[test]
    fn test_get_name_folder() {
        let res = get_name(&Folder(PathBuf::from("..")));
        assert_eq!(res.unwrap(), "src".to_string());
    }
}