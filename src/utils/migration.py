"""Configuration migration utilities for transitioning from vox to vox."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.utils.errors import ConfigurationError


def detect_old_config() -> Optional[Path]:
    """Check if old vox configuration exists.
    
    Returns:
        Path to old vox config directory if found, None otherwise
        
    Raises:
        ConfigurationError: If APPDATA environment variable is not set
    """
    import os
    
    appdata = os.getenv("APPDATA")
    if not appdata:
        raise ConfigurationError(
            "APPDATA environment variable not set",
            error_code="APPDATA_NOT_FOUND",
            context={"platform": "Windows"}
        )
    
    old_config_dir = Path(appdata) / "vox"
    
    if old_config_dir.exists() and old_config_dir.is_dir():
        return old_config_dir
    
    return None


def backup_old_config(old_config_dir: Path) -> Path:
    """Create timestamped backup of old configuration.
    
    Args:
        old_config_dir: Path to old vox configuration directory
        
    Returns:
        Path to backup directory
        
    Raises:
        ConfigurationError: If backup creation fails
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = old_config_dir.parent / f"vox_backup_{timestamp}"
    
    try:
        shutil.copytree(old_config_dir, backup_dir)
        return backup_dir
    except (OSError, shutil.Error) as e:
        raise ConfigurationError(
            f"Failed to create backup of old configuration: {e}",
            error_code="BACKUP_FAILED",
            context={"old_config_dir": str(old_config_dir), "backup_dir": str(backup_dir)}
        )


def copy_config_files(old_config_dir: Path, new_config_dir: Path) -> dict[str, bool]:
    """Copy configuration files from old to new directory.
    
    Migrates:
    - config.json (if exists)
    - sessions/ directory (if exists)
    - models/ directory (if exists)
    
    Args:
        old_config_dir: Path to old vox configuration directory
        new_config_dir: Path to new vox configuration directory
        
    Returns:
        Dict mapping copied items to success status
        
    Raises:
        ConfigurationError: If critical configuration copy fails
    """
    results = {}
    
    # Ensure new config directory exists
    new_config_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy config.json if it exists
    old_config_file = old_config_dir / "config.json"
    new_config_file = new_config_dir / "config.json"
    
    if old_config_file.exists():
        try:
            # Read old config and update app name if present
            with open(old_config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update any vox references to vox
            if isinstance(config_data, dict) and "app_name" in config_data:
                config_data["app_name"] = "vox"
            
            with open(new_config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            results["config.json"] = True
        except (OSError, json.JSONDecodeError) as e:
            raise ConfigurationError(
                f"Failed to copy config.json: {e}",
                error_code="CONFIG_COPY_FAILED",
                context={"file": "config.json"}
            )
    else:
        results["config.json"] = False
    
    # Copy sessions directory if it exists
    old_sessions = old_config_dir / "sessions"
    new_sessions = new_config_dir / "sessions"
    
    if old_sessions.exists() and old_sessions.is_dir():
        try:
            shutil.copytree(old_sessions, new_sessions, dirs_exist_ok=True)
            results["sessions/"] = True
        except (OSError, shutil.Error) as e:
            raise ConfigurationError(
                f"Failed to copy sessions directory: {e}",
                error_code="SESSIONS_COPY_FAILED",
                context={"directory": "sessions/"}
            )
    else:
        results["sessions/"] = False
    
    # Copy models directory if it exists
    old_models = old_config_dir / "models"
    new_models = new_config_dir / "models"
    
    if old_models.exists() and old_models.is_dir():
        try:
            shutil.copytree(old_models, new_models, dirs_exist_ok=True)
            results["models/"] = True
        except (OSError, shutil.Error) as e:
            # Models directory is not critical - log but don't fail
            results["models/"] = False
    else:
        results["models/"] = False
    
    return results


def migrate_config() -> dict[str, any]:
    """Migrate configuration from vox to vox.
    
    This is the main entry point for configuration migration.
    Performs the following steps:
    1. Detect old vox configuration
    2. Create backup of old configuration
    3. Copy files to new vox configuration directory
    4. Report migration results
    
    Returns:
        Dict with migration results including:
        - migrated: bool (True if migration was performed)
        - backup_path: Optional[str] (path to backup if created)
        - copied_files: dict (files successfully copied)
        
    Raises:
        ConfigurationError: If migration fails at any critical step
    """
    import os
    
    # Check for old configuration
    old_config_dir = detect_old_config()
    
    if not old_config_dir:
        return {
            "migrated": False,
            "backup_path": None,
            "copied_files": {},
            "message": "No old vox configuration found"
        }
    
    # Get new config directory path
    appdata = os.getenv("APPDATA")
    new_config_dir = Path(appdata) / "vox"
    
    # If new config already exists, skip migration
    if new_config_dir.exists() and (new_config_dir / "config.json").exists():
        return {
            "migrated": False,
            "backup_path": None,
            "copied_files": {},
            "message": "vox configuration already exists, skipping migration"
        }
    
    # Create backup
    backup_path = backup_old_config(old_config_dir)
    
    # Copy configuration files
    copied_files = copy_config_files(old_config_dir, new_config_dir)
    
    return {
        "migrated": True,
        "backup_path": str(backup_path),
        "copied_files": copied_files,
        "message": f"Successfully migrated configuration from {old_config_dir} to {new_config_dir}"
    }
