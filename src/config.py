import json
from dataclasses import dataclass
from typing import List

from .utils import pub_config_dir


@dataclass
class Config:
	"""Main application configuration"""

	token: str
	chat_ids: List[int]

	@classmethod
	def default(cls) -> "Config":
		return cls(token="", chat_ids=[])

	def to_json(self) -> dict:
		"""Serialize config to JSON-compatible dict"""
		return {"TOKEN": self.token, "CHAT_ID": self.chat_ids}

	@classmethod
	def from_json(cls, data: dict) -> "Config":
		"""Deserialize config from JSON dict"""
		return cls(token=data.get("TOKEN", ""), chat_ids=data.get("CHAT_ID", []))


def pub_load_config() -> Config:
	"""Load config from XDG_CONFIG_HOME/APP_NAME.json"""
	path = pub_config_dir()
	try:
		with open(path, "r") as file:
			data = json.load(file)
			config = Config.from_json(data)
	except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
		print(f"Error loading JSON: {e}")
		config = Config.default()
		with open(path, "w") as file:
			json.dump(config.to_json(), file, indent=2)
			print(f"Created a default config at {path}")

	# Validate required fields
	if not config.token:
		raise ValueError("Token not found or empty!")

	return config
