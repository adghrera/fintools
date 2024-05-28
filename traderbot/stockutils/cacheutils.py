import os
import pickle
import time

from stockutils.config import CACHE_DIR


class AppCache(object):

    def __init__(self, cachename="cache.pickle"):
        self._cache = dict()
        self._cache["created"] = int(time.time())
        self.cachename = cachename

    def get(self, key):
        return self._cache.get(key)

    def getCache(self):
        return self._cache

    def set(self, key, value):
        self._cache["modified"] = int(time.time())
        self._cache[key] = value

    def clear(self):
        self._cache["modified"] = int(time.time())
        self._cache = dict()

    def saveToDisk(self):
        self._cache["saved"] = int(time.time())
        pickle.dump(self._cache, open(CACHE_DIR + self.cachename + ".pickle", "wb"))

    def loadFromDisk(self, oldest=0):
        if os.path.exists(CACHE_DIR + self.cachename + ".pickle"):
            if self._cache["created"] > time.time() - oldest:
                self._cache = pickle.load(
                    open(CACHE_DIR + self.cachename + ".pickle", "rb")
                )
                self._cache["loaded"] = int(time.time())
                return True
            else:
                self._cache = dict()
                self._cache["created"] = int(time.time())
        return False

    def created(self):
        return self.get("created")

    def loadedFromDisk(self):
        return self.get("loaded")
