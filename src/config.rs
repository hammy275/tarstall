use crate::db::{Database, empty_db};
use crate::task::run_task;
use crate::tasks::fs_create::{CreateType, FsCreate};
use crate::tasks::read_file::ReadFile;
use crate::util::home_dir;
use crate::{db, tasks};
use std::env;
use std::path::{Path, PathBuf};
use std::sync::{OnceLock, RwLock, RwLockWriteGuard};

/// tarstall's user-facing version number
pub static VERSION: &str = "2.0.0";
/// The database version tarstall uses. Should be incremented whenever tarstall needs to perform
/// database changes.
pub static FILE_VERSION: u32 = 22;
/// The internal program version tarstall uses. Should be incremented whenever tarstall as a
/// program updates.
pub static INTERNAL_PROGRAM_VERSION: u32 = 144;
/// Mutex holding the database. Should call load() before accessing.
/// Safe to simply unwrap(), as if that fails, then we've already panic()'d.
pub static DB: RwLock<Database> = RwLock::new(empty_db());
/// Path to tarstall home directory. Should call load() before accessing.
static HOME: OnceLock<&Path> = OnceLock::new();

/// Load the database and prepare tarstall for use.
pub fn load() -> Result<(), String> {
    let tarstall_root: PathBuf;
    if let Some(path_str) = env::var("TARSTALL_DIR").ok() {
        tarstall_root = PathBuf::from(path_str);
    } else {
        tarstall_root = home_dir().join(".tarstall");
    }
    // We leak the box here, bringing its memory out. This is usually bad, but since we're keeping
    // this path around for the rest of the program, this is very much intended behavior.
    HOME.set(Box::leak(Box::new(tarstall_root.clone()))).unwrap();
    if !tarstall_root.exists() {
        if let Err(err) = run_task( &FsCreate{ path: tarstall_root.clone(), create_type: CreateType::FOLDER }) {
            return Err(err)
        };
    }
    let db_path = tarstall_root.join("database");
    if db_path.exists() {
        let read_task = ReadFile::create(db_path.clone());
        if let Err(err) = run_task(&read_task) {
            return Err(err)
        }
        match db::deserialize(read_task.contents.get().unwrap()) {
            Some(database) => {
                let mut db = DB.write().unwrap();
                *db = database;
                if let Err(err) = save_db(db) {
                    return Err(err)
                }
            }
            None => return Err("Failed to deserialize database.".to_string())
        }
    } else {
        if let Err(err) = run_task( &FsCreate{ path: db_path.clone(), create_type: CreateType::FILE }) {
            return Err(err)
        };
        let db = DB.write().unwrap();
        if let Err(err) = save_db(db) {
            return Err(err)
        };
    }
    Ok(())
}

/// Get tarstall's home directory.
pub fn tarstall_home() -> &'static Path {
    // Safe to unwrap, should already be set from load().
    HOME.get().unwrap()
}

pub fn save_db(db: RwLockWriteGuard<Database>) -> Result<(), String> {
    match db::serialize(&db) {
        Some(str) => {
            let db_path = tarstall_home().join("database");
            let save_task = tasks::write_file::WriteFile::create(db_path, str);
            run_task(&save_task)
        },
        None => Err("Failed to serialize database".to_string())
    }
}