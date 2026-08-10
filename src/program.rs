use std::fmt::{Display, Formatter};
use std::path::Path;
use serde_json::Value;

/// Represents a single installed program via tarstall.
pub struct Program {
    /// The name of the program. This is also the name of the folder within the tarstall directory
    /// where this program is installed.
    pub name: String,
    /// The type of program installed.
    pub install_type: InstallType,
    /// The list of shortcut paths the program has.
    pub shortcut_paths: Vec<Box<Path>>,
    /// An optional script to run after a program update.
    pub post_update_script: Option<Box<Path>>,
    /// An optional URL to pull updates from. Not used with the GIT install type.
    pub update_url: Option<Box<Path>>,
    /// Whether the program has been added to PATH.
    pub in_path: bool,
    /// The list of paths pointed to by binlinks.
    pub binlinks: Vec<Box<Path>>,
    /// The file extension for ARCHIVE programs' archive type.
    pub update_archive_type: str,
}

impl Display for Program {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name)
    }
}

/// The method of how the program was installed and is kept up-to-date.
pub enum InstallType {
    /// Program was installed from an archive and is not a single file when extracted.
    ARCHIVE,
    /// Program was installed via git.
    GIT,
    /// Program is a single file when extracted.
    SINGLE,
}