"""Unit tests for MaxINIBackupManager."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.modules.maxini_backup import MaxINIBackup, MaxINIBackupManager


@pytest.fixture
def sample_ini() -> Path:
    """Create a temporary ini file for testing."""
    content = "[Test]\nkey=value\n"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ini", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink(missing_ok=True)
    # Cleanup any backups
    for backup in temp_path.parent.glob(f"{temp_path.name}.backup.*"):
        backup.unlink(missing_ok=True)


def test_backup_manager_init() -> None:
    """Test backup manager initialization."""
    manager = MaxINIBackupManager()
    assert manager.max_backups == 10

    manager_custom = MaxINIBackupManager(max_backups=5)
    assert manager_custom.max_backups == 5


def test_create_backup(sample_ini: Path) -> None:
    """Test creating a backup."""
    manager = MaxINIBackupManager()
    backup = manager.create_backup(sample_ini, reason="test_backup")

    assert backup.file_path.exists()
    assert backup.original_path == sample_ini
    assert backup.file_size > 0
    assert backup.checksum != ""
    assert backup.created_by == "test_backup"
    assert isinstance(backup.timestamp, datetime)

    # Cleanup
    backup.file_path.unlink()


def test_create_backup_nonexistent_file() -> None:
    """Test creating backup of non-existent file raises error."""
    manager = MaxINIBackupManager()
    with pytest.raises(FileNotFoundError):
        manager.create_backup(Path("nonexistent.ini"))


def test_list_backups(sample_ini: Path) -> None:
    """Test listing backups."""
    manager = MaxINIBackupManager()

    # Create multiple backups
    backup1 = manager.create_backup(sample_ini, reason="backup1")
    backup2 = manager.create_backup(sample_ini, reason="backup2")

    backups = manager.list_backups(sample_ini)

    assert len(backups) >= 2
    # Should be sorted by timestamp, newest first
    assert backups[0].timestamp >= backups[1].timestamp

    # Cleanup
    for backup in backups:
        backup.file_path.unlink(missing_ok=True)


def test_verify_backup(sample_ini: Path) -> None:
    """Test backup verification."""
    manager = MaxINIBackupManager()
    backup = manager.create_backup(sample_ini)

    # Valid backup should verify
    assert manager.verify_backup(backup)

    # Modify backup file to corrupt it
    with open(backup.file_path, "a", encoding="utf-8") as f:
        f.write("corrupted")

    # Corrupted backup should fail verification
    assert not manager.verify_backup(backup)

    # Cleanup
    backup.file_path.unlink()


def test_restore_backup(sample_ini: Path) -> None:
    """Test restoring from backup."""
    manager = MaxINIBackupManager()

    # Create backup
    backup = manager.create_backup(sample_ini)

    # Modify original file
    with open(sample_ini, "w", encoding="utf-8") as f:
        f.write("[Modified]\nkey=new_value\n")

    # Restore backup
    restored_path = manager.restore_backup(backup)

    assert restored_path == sample_ini

    # Verify restored content
    with open(sample_ini, encoding="utf-8") as f:
        content = f.read()
        assert "Test" in content
        assert "Modified" not in content

    # Cleanup
    for backup_file in sample_ini.parent.glob(f"{sample_ini.name}.backup.*"):
        backup_file.unlink(missing_ok=True)


def test_cleanup_old_backups(sample_ini: Path) -> None:
    """Test auto-cleanup of old backups."""
    manager = MaxINIBackupManager(max_backups=3)

    # Create more backups than max_backups
    for i in range(5):
        manager.create_backup(sample_ini, reason=f"backup{i}")

    backups = manager.list_backups(sample_ini)

    # Should only keep max_backups (3)
    assert len(backups) <= 3

    # Cleanup
    for backup in backups:
        backup.file_path.unlink(missing_ok=True)


def test_delete_backup(sample_ini: Path) -> None:
    """Test deleting a backup."""
    manager = MaxINIBackupManager()
    backup = manager.create_backup(sample_ini)

    assert backup.file_path.exists()

    # Delete backup
    result = manager.delete_backup(backup)

    assert result is True
    assert not backup.file_path.exists()

    # Deleting again should return False
    result = manager.delete_backup(backup)
    assert result is False

