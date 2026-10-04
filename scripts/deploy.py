import logging
import os
import re
import shutil
import sys
import zipfile
import subprocess
from pathlib import Path
import paramiko
from datetime import datetime  # Internal implementation note: legacy behavior is preserved during modernization.

# Internal implementation note: legacy behavior is preserved during modernization.
WORK_DIR: Path = Path(os.getenv("DEPLOY_WORK_DIR", "."))                   # Internal implementation note: legacy behavior is preserved during modernization.
DEST_DIR: Path = WORK_DIR / os.getenv("DEPLOY_BACKUP_DIR", "backups")            # Internal implementation note: legacy behavior is preserved during modernization.
REMOTE: str = os.getenv("REMOTE_HOST", "")
REMOTE_USER: str = os.getenv("REMOTE_USER", "")
REMOTE_PASS: str = os.getenv("REMOTE_PASS", "")
REMOTE_DEST: str = os.getenv("REMOTE_UPLOAD_DIR", "/tmp")
REMOTE_DEPLOY_DIR: str = os.getenv("REMOTE_DEPLOY_DIR", "/opt/telegram-bot-platform")
ZIP_PREFIX: str = os.getenv("DEPLOY_ZIP_PREFIX", "telegram-bot-platform")
EXCLUDE_DIRS = {".git", os.getenv("DEPLOY_BACKUP_DIR", "backups"), ".vscode", "venv", "Testing", "Optimizer", ".pytest_cache", "__pycache__"}
EXCLUDE_FILES = {".gitignore", "deploy_lotus.py", "thread_manager.log", "Run.py", "*.zip"}
# ----------------------------------- #

# Internal implementation note: legacy behavior is preserved during modernization.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
# ---------------------------------- #


def safe_chdir(path: Path) -> None:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        os.chdir(path)
        logging.info("Changed directory to %s", path)
    except Exception as err:
        logging.error("Cannot change directory: %s", err)
        raise


def ensure_dir(path: Path) -> None:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as err:
        logging.error("Cannot create directory %s: %s", path, err)
        raise


def cleanup_old_zips(directory: Path) -> None:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        removed = 0
        for zfile in directory.glob("*.zip"):
            zfile.unlink()
            removed += 1
        logging.info("Removed %d old zip(s)", removed)
    except Exception as err:
        logging.error("Zip cleanup failed: %s", err)
        raise


def get_git_changes_count_since_last_tag(last_version: tuple) -> int:
    """Legacy-compatible behavior preserved for this callable."""
    tag = f"v{last_version[0]}.{last_version[1]:02d}.{last_version[2]}"
    try:
        out = subprocess.check_output(
            ["git", "rev-list", "--count", f"{tag}..HEAD"],
            cwd=WORK_DIR,
            stderr=subprocess.DEVNULL,
        )
        return int(out.strip())
    except subprocess.CalledProcessError:
        # Internal implementation note: legacy behavior is preserved during modernization.
        out = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=WORK_DIR)
        return int(out.strip())


def compute_next_semver(dest_dir: Path) -> tuple:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        ensure_dir(dest_dir)  # Internal implementation note: legacy behavior is preserved during modernization.
        pattern = re.compile(rf"{re.escape(ZIP_PREFIX)}(\d+)\.(\d+)\.(\d+)\.zip", re.I)
        versions = []
        for f in dest_dir.glob(f"{ZIP_PREFIX}*.*.*.zip"):
            if (m := pattern.match(f.name)):
                versions.append(tuple(map(int, m.groups())))
        last = max(versions) if versions else (3, 0, 0)

        changes = get_git_changes_count_since_last_tag(last)
        major, minor, patch = last
        total_patch = patch + changes
        extra_minor, patch = divmod(total_patch, 10)
        minor += extra_minor
        extra_major, minor = divmod(minor, 100)
        major += extra_major
        return major, minor, patch
    except Exception as err:
        logging.error("Semantic version calculation failed: %s", err)
        raise


def build_zip(src_dir: Path, zip_path: Path) -> None:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(src_dir):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                rel_root = Path(root).relative_to(src_dir)
                for fname in files:
                    if fname in EXCLUDE_FILES or fname == "__init__.py":
                        continue
                    fpath = Path(root) / fname
                    zf.write(fpath, rel_root / fname)
        logging.info("Zip %s created successfully", zip_path.name)
    except Exception as err:
        logging.error("Zip creation failed: %s", err)
        raise


def move_zip(src_zip: Path, dest_dir: Path) -> Path:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        ensure_dir(dest_dir)
        dest_zip = dest_dir / src_zip.name
        shutil.move(src_zip, dest_zip)
        logging.info("Moved zip to %s", dest_zip)
        return dest_zip
    except Exception as err:
        logging.error("Moving zip failed: %s", err)
        raise


def transfer_remote(local_zip: Path) -> None:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        logging.info("Connecting to %s …", REMOTE)
        transport = paramiko.Transport((REMOTE, 22))
        transport.connect(username=REMOTE_USER, password=REMOTE_PASS)
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            remote_path = f"{REMOTE_DEST}/{local_zip.name}"
            sftp.put(local_zip.as_posix(), remote_path)
            logging.info("Uploaded %s to %s", local_zip.name, remote_path)
        transport.close()
    except Exception as err:
        logging.error("SCP transfer failed: %s", err)
        raise


def remote_deploy(zip_name: str) -> None:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        logging.info("Starting remote deployment …")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(REMOTE, username=REMOTE_USER, password=REMOTE_PASS)

        client.exec_command(f"mkdir -p {REMOTE_DEPLOY_DIR}")

        unzip_cmd = f"unzip -o {REMOTE_DEST}/{zip_name} -d {REMOTE_DEPLOY_DIR}"
        client.exec_command(unzip_cmd)[1].channel.recv_exit_status()
        logging.info("Unzipped archive on remote")

        compose_cmd = f"cd {REMOTE_DEPLOY_DIR} && docker compose restart"
        client.exec_command(compose_cmd)[1].channel.recv_exit_status()
        logging.info("Docker Compose restarted")

        client.close()
    except Exception as err:
        logging.error("Remote deployment failed: %s", err)
        raise


def main() -> None:
    """Legacy-compatible behavior preserved for this callable."""
    try:
        safe_chdir(WORK_DIR)
        ensure_dir(DEST_DIR)
        cleanup_old_zips(WORK_DIR)

        # Internal implementation note: legacy behavior is preserved during modernization.
        major, minor, patch = compute_next_semver(DEST_DIR)
        version_str = f"{major}.{minor:02d}.{patch}"

        # Internal implementation note: legacy behavior is preserved during modernization.
        commit_message = f"Bot Version: {version_str}"
        try:
            subprocess.check_call(["git", "add", "-A"], cwd=WORK_DIR)
            subprocess.check_call(["git", "commit", "-m", commit_message], cwd=WORK_DIR)
            logging.info("Git commit created: %s", commit_message)
        except subprocess.CalledProcessError:
            logging.warning("No changes to commit for version %s", version_str)

        # Internal implementation note: legacy behavior is preserved during modernization.
        zip_name = f"{ZIP_PREFIX}{version_str}.zip"
        temp_zip_path = WORK_DIR / zip_name

        build_zip(WORK_DIR, temp_zip_path)
        final_zip = move_zip(temp_zip_path, DEST_DIR)

        transfer_remote(final_zip)
        remote_deploy(final_zip.name)

        logging.info("Deployment finished successfully ✔")
    except Exception as fatal:
        logging.critical("Process aborted: %s", fatal)
        sys.exit(1)


if __name__ == "__main__":
    main()
