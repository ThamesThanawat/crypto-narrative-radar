"""Project path configuration for Crypto Narrative Radar."""

from pathlib import Path

# Project root directory (repository root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Output and template directories
REPORTS_DIR = PROJECT_ROOT / "reports"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
