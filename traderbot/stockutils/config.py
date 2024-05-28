import logging
import os
import json

TMP_DIR = "/tmp/data/traderbot/tmp"
CONFIG_FILE = TMP_DIR + "/config.json"
TICKERS = TMP_DIR + "/tickers.json"
RAW_TICKERS = TMP_DIR + "/raw_tickers.json"
CACHE_DIR = TMP_DIR + "/cache/"


class ConfigManager:

    def __init__(self):
        self._conf = None

    def get_config(self, name: str, default_value=None):
        conf = self.load_config()
        return conf.get(name, default_value)

    def set_config(self, name, value):
        conf = self.load_config()
        conf[name] = value
        with open(CONFIG_FILE, "w") as f:
            json.dump(conf, f)

    def load_config(self) -> dict:
        if not self._conf:
            if os.path.exists(CONFIG_FILE):
                logging.debug("reading config file")
                with open(CONFIG_FILE, "r") as f:
                    self._conf = json.load(f)
            else:
                logging.warning("Missing config file")
                return {}

        return self._conf
