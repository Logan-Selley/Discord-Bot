import toml
import logging
import os
import json

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
"yt_user"=None
"yt_pass"=None
[APIs]
# Other APIs
"forcastio"=""
[Moderation]
# Moderation settings
"warns_till_kick"=3
"warns_till_ban"=5
"""
warn_path = "./warnings.json"
config_path = "./config.toml"
temp_punish = "./punish.json"


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
        with open(path, encoding='utf-8') as f:
            warnings = json.load(f)
    else:
        warnings = {}
        warnings['guilds'] = []
    return warnings


def load_punish(path=temp_punish):
    """Loads or creates temp punishment file from path"""
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            punishments = json.load(f)
    else:
        punishments = {}
        punishments['guilds'] = []
    return punishments

