use serde::{Deserialize, Serialize};
use serde_json::{from_str, json, Value, to_string};
use crate::program::Program;

/// The database version tarstall uses. Should be incremented whenever tarstall needs to perform
/// database changes.
pub static FILE_VERSION: u32 = 22;
/// The internal program version tarstall uses. Should be incremented whenever tarstall as a
/// program updates.
pub static INTERNAL_PROGRAM_VERSION: u32 = 144;

/// The in-memory representation of tarstall's database.
#[derive(Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct Database {
    pub options: Options,
    pub version: Version,
    pub programs: Vec<Program>
}

/// The tarstall-wide options.
#[derive(Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct Options {
    pub verbose: bool,
    pub auto_install: bool,
    pub shell_file: Option<String>,
    pub skip_questions: bool,
    pub update_url_programs: bool,
    pub press_enter_key: bool
}

/// tarstall version information as stored in the database. When the database initially loads, the
/// version numbers here may not correspond to the current tarstall version.
#[derive(Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct Version {
    pub file_version: u32,
    pub program_internal_version: u32,
    pub branch: String
}

/// Retrieve a database used to represent a database that hasn't been loaded yet.
pub const fn empty_db() -> Database {
    Database{
        options: Options {
            verbose: false,
            auto_install: false,
            shell_file: None,
            skip_questions: false,
            update_url_programs: false,
            press_enter_key: true,
        },
        version: Version {
            file_version: FILE_VERSION,
            program_internal_version: INTERNAL_PROGRAM_VERSION,
            branch: String::new(),
        },
        programs: Vec::new(),
    }
}

/// Retrieve a copy of the default database for fresh tarstall installations.
pub fn default_db() -> Database {
    Database{
        options: Options {
            verbose: false,
            auto_install: false,
            shell_file: todo!("Need to determine shell file based on shell configuration on *nix"),
            skip_questions: false,
            update_url_programs: false,
            press_enter_key: true,
        },
        version: Version {
            file_version: FILE_VERSION,
            program_internal_version: INTERNAL_PROGRAM_VERSION,
            branch: "main".to_string(),
        },
        programs: Vec::new(),
    }
}

/// Serialize a database to JSON.
pub fn serialize(db: &Database) -> Option<String> {
    serde_json::to_string_pretty(db).ok()
}

/// Deserialize a database from JSON.
pub fn deserialize(json_str: &str) -> Option<Database> {
    if let Ok(db) = from_str(json_str) {
        return Some(db)
    };
    // Try de-serializing to old (tarstall 1.x) format
    let Ok(Value::Object(json)) = from_str(json_str) else {
        return None
    };
    let mut programs: Vec<Program> = Vec::new();
    for program_json in json.get("programs")?.as_object()? {
        let name = program_json.0;
        let program = Program::old_deserialize(program_json.1.as_object()?, name)?;
        programs.push(program);
    }
    let options = json.get("options")?.as_object()?;
    let version = json.get("version")?.as_object()?;
    Some(Database{
        options: Options {
            verbose: options.get("Verbose")?.as_bool()?,
            auto_install: options.get("AutoInstall")?.as_bool()?,
            shell_file: Some(options.get("ShellFile")?.as_str()?.to_string()),
            skip_questions: options.get("SkipQuestions")?.as_bool()?,
            update_url_programs: options.get("UpdateURLPrograms")?.as_bool()?,
            press_enter_key: options.get("PressEnterKey")?.as_bool()?,
        },
        version: Version {
            file_version: u32::try_from(version.get("file_version")?.as_u64()?).ok()?,
            program_internal_version: u32::try_from(version.get("prog_internal_version")?.as_u64()?).ok()?,
            branch: version.get("branch")?.as_str()?.to_string(),
        },
        programs,
    })
}

#[cfg(test)]
mod tests {
    use crate::db::{deserialize, Database, Options, Version};
    use crate::program::{InstallType, Program};

    #[test]
    fn test_old_db_deserialize() {
        let old_db = "{
            \"options\": {
                \"Verbose\": false,
                \"AutoInstall\": false,
                \"ShellFile\": \".zshrc\",
                \"SkipQuestions\": false,
                \"UpdateURLPrograms\": false,
                \"PressEnterKey\": true
            },
            \"version\": {
                \"file_version\": 21,
                \"prog_internal_version\": 142,
                \"branch\": \"master\"
            },
            \"programs\": {
                \"archive_program\": {
                    \"install_type\": \"default\",
                    \"desktops\": [],
                    \"post_upgrade_script\": null,
                    \"update_url\": \"https://example.com/archive_program.tar.gz\",
                    \"has_path\": false,
                    \"binlinks\": [],
                    \"update_archive_type\": \".tar.gz\"
                },
                \"comp-status\": {
                    \"install_type\": \"git\",
                    \"desktops\": [],
                    \"post_upgrade_script\": null,
                    \"update_url\": null,
                    \"has_path\": false,
                    \"binlinks\": []
                },
                \"fake_appimage\": {
                    \"install_type\": \"single\",
                    \"desktops\": [],
                    \"post_upgrade_script\": null,
                    \"update_url\": null,
                    \"has_path\": false,
                    \"binlinks\": []
                }
            }
        }";
        let db = deserialize(old_db).unwrap();
        assert_eq!(db, Database{
            options: Options {
                verbose: false,
                auto_install: false,
                shell_file: Some(".zshrc".to_string()),
                skip_questions: false,
                update_url_programs: false,
                press_enter_key: true,
            },
            version: Version {
                file_version: 21,
                program_internal_version: 142,
                branch: "master".to_string(),
            },
            programs: vec![
                Program{
                    name: "archive_program".to_string(),
                    install_type: InstallType::ARCHIVE {update_archive_type: ".tar.gz".to_string()},
                    shortcut_paths: Vec::new(),
                    post_update_script: None,
                    update_url: Some("https://example.com/archive_program.tar.gz".to_string()),
                    in_path: false,
                },
                Program{
                    name: "comp-status".to_string(),
                    install_type: InstallType::GIT,
                    shortcut_paths: Vec::new(),
                    post_update_script: None,
                    update_url: None,
                    in_path: false,
                },
                Program{
                    name: "fake_appimage".to_string(),
                    install_type: InstallType::SINGLE,
                    shortcut_paths: Vec::new(),
                    post_update_script: None,
                    update_url: None,
                    in_path: false,
                },
            ],
        })
    }
}