import toml
import logging
import os
import json

EXAMPLE_CONFIG = """\"token\"=\"\" # the bot's token
[music]
# Lyrics search engine keys:
"search_key"=""
"search_id"=""
# Spotify API keys:
\"spotify_client\"=\"\"
\"spotify_secret\"=\"\"
[APIs]
# Other APIs
"forcastio"=""
"bitly_id"=""
"bitly_secret"=""
"""
warn_path = "./warnings.json"
config_path = "./config.toml"
temp_punish = "./punish.json"
xp_path = "./experience.json"
settings_path = "./settings.json"


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


def load_xp(path=xp_path):
    """Loads or creates temp punishment file from path"""
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            exp = json.load(f)
    else:
        exp = {}
        exp['guilds'] = {}
    return exp


def load_settings(path=settings_path):
    """Loads or creates settings file from path"""
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}
        settings['guilds'] = {}
    return settings

