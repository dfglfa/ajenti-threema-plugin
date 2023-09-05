import yaml
import logging

CONFIG_PATH = "/etc/linuxmuster/webui/threema.yml"


def _loadConfig():
    try:
        with open(CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)
            return config
    except:
        logging.exception(f"Could not load config from {CONFIG_PATH}")


def getThreemaApiKey():
    config = _loadConfig()
    return config.get("threema_api_key")


def getStudentsFileName():
    config = _loadConfig()
    return config.get("students_data_file")


def getThreemaBroadcastId():
    config = _loadConfig()
    return config.get("threema_broadcast_id")


def getThreemaBroadcastApiKey():
    config = _loadConfig()
    return config.get("threema_broadcast_api_key")
