use std::fmt::{Display, Formatter};
use std::path::{PathBuf};
use serde::{Deserialize, Serialize};
use serde_json::{Value, Map, from_value, to_value};
use crate::util::home_dir;

/// Represents a single installed program via tarstall.
#[derive(Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Program {
    /// The name of the program. This is also the name of the folder within the tarstall directory
    /// where this program is installed.
    pub name: String,
    /// The type of program installed.
    pub install_type: InstallType,
    /// The list of shortcut paths the program has.
    pub shortcut_paths: Vec<PathBuf>,
    /// An optional script to run after a program update.
    pub post_update_script: Option<PathBuf>,
    /// An optional URL to pull updates from. Not used with the GIT install type.
    pub update_url: Option<String>,
    /// Whether the program has been added to PATH.
    pub in_path: bool,
}

impl Display for Program {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name)
    }
}

impl Program {
    pub fn old_deserialize(json: &Map<String, Value>, name: &str) -> Option<Program> {
        let install_type = match json.get("install_type")?.as_str()? {
            "default" => {
                let update_archive_type = json.get("update_archive_type")?.as_str()?;
                InstallType::ARCHIVE{update_archive_type: update_archive_type.to_string()}
            }
            "git" => InstallType::GIT,
            "single" => InstallType::SINGLE,
            _ => return None
        };
        let mut shortcut_paths: Vec<PathBuf> = Vec::new();
        let Some(Value::Array(desktops)) = json.get("desktops") else {
            return None
        };
        let home = home_dir();
        for maybe_desktop in desktops {
            let Value::String(desktop) = maybe_desktop else {
                return None
            };
            shortcut_paths.push(home
                .join(".local")
                .join("share")
                .join("applications")
                .join("tarstall")
                .join(desktop)
                .with_extension(".desktop"))
        }
        // Post-update script
        let post_update_script: Option<PathBuf>;
        if let Some(value) = json.get("post_upgrade_script") {
            match value {
                Value::Null => post_update_script = None,
                Value::String(path_str) => match path_str.parse::<PathBuf>() {
                    Ok(path) => post_update_script = Some(path),
                    Err(_) => return None
                }
                _ => return None
            }
        } else {
            return None
        }
        // Update URL
        let update_url = match json.get("update_url") {
            Some(Value::Null) => None,
            Some(Value::String(url)) => Some(url.to_string()),
            _ => return None
        };
        let in_path;
        if let Some(Value::Bool(res)) = json.get("has_path") {
            in_path = *res
        } else if let Some(Value::Bool(res)) = json.get("in_path") {
            in_path = *res
        } else {
            return None
        }
        Some(Program{
            name: name.to_string(),
            install_type,
            shortcut_paths,
            post_update_script,
            update_url,
            in_path
        })
    }
}

/// The method of how the program was installed and is kept up-to-date.
#[derive(Debug, PartialEq, Eq, Serialize, Deserialize, Clone)]
pub enum InstallType {
    /// Program was installed from an archive and is not a single file when extracted.
    ARCHIVE{update_archive_type: String},
    /// Program was installed via git.
    GIT,
    /// Program is a single file when extracted.
    SINGLE,
}

#[cfg(test)]
mod tests {
    use std::assert_matches;
    use std::path::PathBuf;
    use std::str::FromStr;
    use serde::Deserialize;
    use serde_json::{Map, Value};
    use crate::program::{Program, InstallType};

    #[test]
    fn test_deserialize_old_tarstall_program() {
        let json_str = "{
            \"install_type\": \"git\",
            \"desktops\": [
                \"install_tarstall-tarstall\"
            ],
            \"post_upgrade_script\": null,
            \"update_url\": null,
            \"has_path\": true,
            \"binlinks\": [
                \"install_tarstall\"
            ]
        }";
        let json: Map<String, Value> = serde_json::from_str(json_str).unwrap();
        let program = Program::old_deserialize(&json, "tarstall").unwrap();
        assert_eq!(program.install_type, InstallType::GIT);
        assert_eq!(program.shortcut_paths.len(), 1);
        assert_matches!(program.post_update_script, None);
        assert_matches!(program.update_url, None);
        assert_matches!(program.in_path, true);
        // No assert for binlinks as we don't have those anymore
    }
}