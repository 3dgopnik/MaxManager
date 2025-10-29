#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaxManager Version Updater
Updates version in single source of truth: src/__version__.py
"""

import sys
from pathlib import Path

def update_version(version: str) -> bool:
    """Update version in __version__.py file."""
    project_root = Path(__file__).parent.parent
    version_file = project_root / "src" / "__version__.py"
    
    if not version_file.exists():
        print(f"ERROR: {version_file} not found!")
        return False
    
    # Read current content
    content = version_file.read_text(encoding='utf-8')
    
    # Replace version
    import re
    new_content = re.sub(
        r'__version__ = "[^"]*"',
        f'__version__ = "{version}"',
        content
    )
    
    # Write back
    if new_content != content:
        version_file.write_text(new_content, encoding='utf-8')
        print(f"✅ Version updated to {version} in {version_file}")
        print("\nNext steps:")
        print("   git add src/__version__.py")
        print(f"   git commit -m 'chore: bump version to {version}'")
        print("   git push origin main")
        return True
    else:
        print(f"⚠️ Version already {version}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_version.py <version>")
        print("Example: python scripts/update_version.py 0.7.0")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Validate version format
    if not version.count('.') == 2:
        print(f"ERROR: Invalid version format '{version}'. Use X.Y.Z format.")
        sys.exit(1)
    
    success = update_version(version)
    sys.exit(0 if success else 1)
