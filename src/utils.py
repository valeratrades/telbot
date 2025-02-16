from .lib import PUB_APP_NAME
from pathlib import Path
import os


def pub_data_dir() -> Path:
	"""Data dir by xdg standard (and whatever windows has)"""

	path: Path = None  # how is this legal
	if os.name == "nt":  # Windows
		# Theoretically should be C:\Users\<username>\AppData\Local\APP_NAME (haven't tested)
		path = Path(os.environ["LOCALAPPDATA"]) / PUB_APP_NAME
	else:  # Linux/Mac
		# ~/.local/share/APP_NAME
		xdg_data_home = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
		path = Path(xdg_data_home) / PUB_APP_NAME

	path.mkdir(parents=True, exist_ok=True)
	return path


def pub_config_dir() -> Path:
	"""Config file path by xdg standard (and whatever windows has)"""
	if os.name == "nt":  # Windows
		# I think it should be C:\Users\<username>\AppData\Roaming\APP_NAME.json
		path = Path(os.environ["APPDATA"]) / f"{PUB_APP_NAME}.json"
	else:  # Linux/Mac
		# ~/.config/APP_NAME.json
		xdg_config_home = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
		path = Path(xdg_config_home) / f"{PUB_APP_NAME}.json"

	path.parent.mkdir(parents=True, exist_ok=True)
	return path
