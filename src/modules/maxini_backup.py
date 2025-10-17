"""MaxINI Backup Manager - Create and manage backups of max.ini files."""

import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class MaxINIBackup:
    """Represents a backup of max.ini file."""

    timestamp: datetime
    file_path: Path
    original_path: Path
    file_size: int
    checksum: str
    created_by: str | None = None


class MaxINIBackupManager:
    """Manager for max.ini backups."""

    def __init__(self, max_backups: int = 10) -> None:
        """
        Initialize backup manager.

        Args:
            max_backups: Maximum number of backups to keep (default: 10)
        """
        self.max_backups = max_backups

    def create_backup(self, ini_path: Path, reason: str | None = None) -> MaxINIBackup:
        """
        Create timestamped backup of max.ini.

        Args:
            ini_path: Path to 3dsMax.ini
            reason: Optional reason (e.g., "preset_applied:high_performance")

        Returns:
            Backup object

        Raises:
            FileNotFoundError: If ini_path doesn't exist
            PermissionError: If can't write to backup location
        """
        if not ini_path.exists():
            raise FileNotFoundError(f"INI file not found: {ini_path}")

        # Generate backup filename with timestamp
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{ini_path.name}.backup.{timestamp_str}"
        backup_path = ini_path.parent / backup_filename

        # Copy file
        shutil.copy2(ini_path, backup_path)

        # Calculate checksum
        checksum = self._calculate_checksum(backup_path)

        # Get file size
        file_size = backup_path.stat().st_size

        backup = MaxINIBackup(
            timestamp=timestamp,
            file_path=backup_path,
            original_path=ini_path,
            file_size=file_size,
            checksum=checksum,
            created_by=reason,
        )

        # Auto cleanup old backups
        self.cleanup_old_backups(ini_path)

        return backup

    def list_backups(self, ini_path: Path) -> list[MaxINIBackup]:
        """
        List all backups for given ini file.

        Args:
            ini_path: Path to 3dsMax.ini

        Returns:
            List of backups (sorted by timestamp, newest first)
        """
        backup_pattern = f"{ini_path.name}.backup.*"
        backup_files = sorted(
            ini_path.parent.glob(backup_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        backups: list[MaxINIBackup] = []

        for backup_file in backup_files:
            # Parse timestamp from filename
            try:
                timestamp_str = backup_file.name.split(".backup.")[1]
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except (IndexError, ValueError):
                # Skip files with invalid format
                continue

            backup = MaxINIBackup(
                timestamp=timestamp,
                file_path=backup_file,
                original_path=ini_path,
                file_size=backup_file.stat().st_size,
                checksum=self._calculate_checksum(backup_file),
                created_by=None,  # Not stored in filename
            )

            backups.append(backup)

        return backups

    def restore_backup(self, backup: MaxINIBackup) -> Path:
        """
        Restore max.ini from backup.

        Args:
            backup: Backup to restore

        Returns:
            Path to restored ini file

        Raises:
            FileNotFoundError: If backup file doesn't exist
        """
        if not backup.file_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup.file_path}")

        # Verify checksum before restore
        if not self.verify_backup(backup):
            raise ValueError(f"Backup file is corrupted: {backup.file_path}")

        # Create backup of current file before restoring
        if backup.original_path.exists():
            self.create_backup(backup.original_path, reason="before_restore")

        # Restore
        shutil.copy2(backup.file_path, backup.original_path)

        return backup.original_path

    def delete_backup(self, backup: MaxINIBackup) -> bool:
        """
        Delete specific backup.

        Args:
            backup: Backup to delete

        Returns:
            True if deleted successfully
        """
        try:
            backup.file_path.unlink()
            return True
        except FileNotFoundError:
            return False

    def cleanup_old_backups(self, ini_path: Path) -> int:
        """
        Auto-cleanup old backups (keep max_backups newest).

        Args:
            ini_path: Path to 3dsMax.ini

        Returns:
            Number of backups deleted
        """
        backups = self.list_backups(ini_path)

        if len(backups) <= self.max_backups:
            return 0

        # Delete oldest backups
        backups_to_delete = backups[self.max_backups :]
        deleted_count = 0

        for backup in backups_to_delete:
            if self.delete_backup(backup):
                deleted_count += 1

        return deleted_count

    def verify_backup(self, backup: MaxINIBackup) -> bool:
        """
        Verify backup integrity using checksum.

        Args:
            backup: Backup to verify

        Returns:
            True if backup is valid
        """
        if not backup.file_path.exists():
            return False

        current_checksum = self._calculate_checksum(backup.file_path)
        return current_checksum == backup.checksum

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

