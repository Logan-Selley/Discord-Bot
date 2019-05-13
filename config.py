import toml
import logging
import os

EXAMPLE_CONFIG = """\"token\"=\"\" # the bot's token
\"prefix\"=\"!\" # prefix used to denote commands
[music]
# Options for the music commands
"max_volume"=250 # Max audio volume. Set to -1 for unlimited.
"search_key"=""
"search_id"=""
"""


def load_config(path="./config.toml"):
    """Loads the config from `path`"""
    if os.path.exists(path) and os.path.isfile(path):
        config = toml.load(path)
        return config
    else:
        with open(path, "w") as config:
            config.write(EXAMPLE_CONFIG)
            logging.warn(
                f"No config file found. Creating a default config file at {path}"
            )
        return load_config(path=path)
