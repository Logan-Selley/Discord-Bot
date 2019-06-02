import toml
import logging
import os

EXAMPLE_CONFIG = """\"token\"=\"\" # the bot's token
\"prefix\"=\"!\" # prefix used to denote commands
[music]
# Options for the music commands
"max_volume"=250 # Max audio volume. Set to -1 for unlimited.
# Lyrics search engine keys:
"search_key"=""
"search_id"=""
# Spotify API keys:
\"spotify_client\"=\"\"
\"spotify_secret\"=\"\"
# Moderation settings
"warns_till_ban"=3
"""
warn_path = "./warnings.toml"
config_path = "./config.toml"


def load_config(path=config_path):
    """Loads the config from `path`"""
    if os.path.exists(path) and os.path.isfile(path):
        config = toml.load(path)
        return config
    else:
        with open(path, "w") as config:
            config.write(EXAMPLE_CONFIG)
            logging.warning(
                f"No config file found. Creating a default config file at {path}"
            )
        return load_config(path=path)


def load_warns(path=warn_path):
    """Loads or creates warning file from path"""
    if os.path.exists(path) and os.path.isfile(path):
        warns = toml.load(path)
        return warns
    else:
        with open(path, "w") as warns:
            logging.warning(f"No warning file found. Creating an empty warning file at {path}")
            return load_warns(path=path)
