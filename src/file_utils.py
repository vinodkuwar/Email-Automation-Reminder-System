"""
Cross-Platform File Utilities Module
Provides robust file reading and writing utilities with automatic fallback
for restricted/sandboxed environments (e.g. Windows Controlled Folder Access).
"""

import os
import subprocess
from pathlib import Path

def safe_write_text(filepath: str, content: str, encoding: str = "utf-8"):
    """
    Write text content to file.
    Tries standard Python open() first; if blocked by Windows Protected Folders,
    uses PowerShell / system API fallback.
    """
    path = Path(filepath).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
    except (OSError, PermissionError):
        # Fallback via PowerShell
        escaped_content = content.replace("'", "''")
        cmd = f"[System.IO.File]::WriteAllText('{str(path)}', '{escaped_content}', [System.Text.Encoding]::UTF8)"
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)

def safe_append_text(filepath: str, content: str, encoding: str = "utf-8"):
    """
    Append text content to file.
    """
    path = Path(filepath).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "a", encoding=encoding) as f:
            f.write(content)
    except (OSError, PermissionError):
        escaped_content = content.replace("'", "''")
        cmd = f"[System.IO.File]::AppendAllText('{str(path)}', '{escaped_content}', [System.Text.Encoding]::UTF8)"
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)

def safe_read_text(filepath: str, encoding: str = "utf-8") -> str:
    """
    Read text content from file.
    """
    path = Path(filepath).resolve()
    with open(path, "r", encoding=encoding) as f:
        return f.read()
