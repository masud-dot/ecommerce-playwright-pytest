"""Load environment and test data with optional environment-variable overrides."""

import json
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def load_json(file_name: str) -> dict[str, Any]:
    path = CONFIG_DIR / file_name
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def get_environment(env_name: str = "qa") -> dict[str, str]:
    environments = load_json("environments.json")
    if env_name not in environments:
        raise ValueError(f"Environment '{env_name}' is not configured")

    environment = dict(environments[env_name])
    environment["base_url"] = os.getenv("BASE_URL", environment["base_url"])
    environment["api_base_url"] = os.getenv("API_BASE_URL", environment["api_base_url"])
    return environment


def get_user(user_type: str) -> dict[str, str]:
    users = load_json("test_data.json").get("users", {})
    if user_type not in users:
        raise ValueError(f"Test user '{user_type}' is not configured")

    user = dict(users[user_type])
    if user_type == "standard_user":
        user["username"] = os.getenv("SAUCEDEMO_USERNAME", user["username"])
        user["password"] = os.getenv("SAUCEDEMO_PASSWORD", user["password"])
    return user


def get_checkout_data() -> dict[str, str]:
    return load_json("test_data.json")["checkout"]
