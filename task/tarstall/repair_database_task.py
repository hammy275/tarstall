import config
import datetime
import file
import os
from shutil import move
from tarstall_manage import get_default_db
from task.task import Task, TaskRunner


class RepairDatabaseTask(Task):
    def run(self, task_runner: TaskRunner):
        """Attempts to Repair Tarstall DB.

            WARNING: THIS SHOULD NOT BE USED UNLESS THE DATABASE CANNOT BE RECOVERED OTHERWISE!!!
            BECAUSE AN EMPTY DATABASE ONLY HAS LIMITED KNOWLEDGE OF PAST OPERATIONS, SEVERAL THINGS CANNOT
            AND WILL NOT BE RECOVERED!!!!!!
            """
        config.vprint("Attempting repair of database...")

        config.vprint("Getting stock database to build off of")
        new_db = get_default_db()
        task_runner.progress(0.05)

        config.vprint("Re-discovering programs:")
        for pf in os.listdir(file.full(f"{config.TARSTALL_DIR}/bin/")):
            config.vprint("Re-discovering " + pf, end="\r")
            prog_info = {pf: {"install_type": "default", "desktops": [],
                              "post_upgrade_script": None, "update_url": None, "has_path": False, "binlinks": []}}
            if ".git" in os.listdir(file.full(f"{config.TARSTALL_DIR}/bin/{pf}")):
                prog_info[pf]["install_type"] = "git"
            elif len(os.listdir(file.full(f"{config.TARSTALL_DIR}/bin/{pf}"))) == 1:
                prog_info[pf]["install_type"] = "single"
            new_db["programs"].update(prog_info)

        task_runner.progress(0.2)

        config.vprint("Reading tarstall's bashrc file for further operations...")
        with open(file.full(f"{config.TARSTALL_DIR}/.bashrc")) as f:
            bashrc_lines = f.readlines()

        task_runner.progress(0.25)

        config.vprint("Re-registering PATHs")
        for l in bashrc_lines:
            if l.startswith("export PATH=$PATH") and '#' in l:
                program = l[l.find("#") + 2:].rstrip()
                config.vprint("Re-registering PATH for " + program, end="\r")
                new_db["programs"][program]["has_path"] = True

        task_runner.progress(0.35)

        config.vprint("Re-registering binlinks")
        for l in bashrc_lines:
            if l.startswith("alias ") and '#' in l:
                program = l[l.find("#") + 2:].rstrip()
                config.vprint("Re-registering a binlink or binlinks for " + program, end="\r")
                binlinked_file = l[6:l.find("=")]
                new_db["programs"][program]["binlinks"].append(binlinked_file)

        task_runner.progress(0.6)

        config.vprint("Backing up old database...")
        date_str = datetime.datetime.today().strftime("%d-%m-%Y-%H-%M-%S")
        move(file.full(f"{config.TARSTALL_DIR}/database"),
             file.full(f"{config.TARSTALL_DIR}/database-backup-{date_str}.bak"))

        task_runner.progress(0.8)

        config.vprint("Re-discovering .desktop files...")
        for d in os.listdir(file.full("~/.local/share/applications/tarstall")):
            # File name: {program}-{package}.desktop
            # Stored in DB as {program}-package
            desktop_name = file.name(
                file.full("~/.local/share/applications/tarstall/{}".format(d)))  # Returns "{program}-{package}"
            desktop_info = desktop_name.split("-")
            new_db["programs"][desktop_info[1]]["desktops"].append("{}-{}".format(desktop_info[0], desktop_info[1]))

        config.vprint("Database repair complete!")
