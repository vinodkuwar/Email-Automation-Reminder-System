"""
Email Template Engine Module
Loads email notification templates and renders personalized messages
with placeholder substitution.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from src.logger_config import logger

def load_template_file(filepath: Optional[str] = None) -> str:
    """
    Load raw template text from file.
    Defaults to templates/reminder_template.txt.
    """
    if filepath is None:
        base_dir = Path(__file__).resolve().parent.parent
        filepath = str(base_dir / "templates" / "reminder_template.txt")

    path = Path(filepath)
    if not path.exists():
        logger.error(f"Template file not found at: {filepath}")
        raise FileNotFoundError(f"Template file does not exist: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    logger.info(f"Loaded template from: {filepath} ({len(content)} characters)")
    return content

class SafeDict(dict):
    """Dictionary that returns the placeholder tag itself or a fallback if key is missing."""
    def __missing__(self, key):
        return f"[{key.upper()}_NOT_PROVIDED]"

def render_template(template_content: str, context: Dict[str, Any]) -> str:
    """
    Personalize an email template with context variables.
    Safe against missing keys: replaces missing placeholders with clean fallback text.
    """
    if not template_content:
        return ""

    # Sanitize and convert all context values to string
    sanitized_context = {str(k): (str(v) if v is not None else "") for k, v in context.items()}
    
    try:
        # Use SafeDict with string formatting to avoid KeyError crashes
        rendered = template_content.format_map(SafeDict(sanitized_context))
        return rendered
    except Exception as e:
        logger.warning(f"Formatting warning in template substitution: {e}")
        # Fallback manual token replacement
        result = template_content
        for key, val in sanitized_context.items():
            result = result.replace(f"{{{key}}}", str(val))
        return result
