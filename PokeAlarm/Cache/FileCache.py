# Standard Library Imports
import os
# 3rd Party Imports
import logging
import pickle
import portalocker
import traceback
# Local Imports
from ..Utils import get_path
from . import Cache

log = logging.getLogger('FileCache')


class FileCache(Cache):

    def __init__(self, name):
        """ Initializes a new cache object for storing data between events. """
        super(FileCache, self).__init__()
        self._name = name
        self._file = get_path(os.path.join("cache", "{}.cache".format(name)))

        log.debug("Checking for previous cache at {}".format(self._file))
        if os.path.isfile(self._file):
            self._load()
        else:
            with portalocker.Lock(self._file, mode="wb+") as f:
                pickle.dump({}, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load(self):
        try:
            with portalocker.Lock(self._file, mode="rb") as f:
                data = pickle.load(f)
                self._mon_hist = data.get('mon_hist', {})
                self._stop_hist = data.get('stop_hist', {})
                self._egg_hist = data.get('egg_hist', {})
                self._raid_hist = data.get('raid_hist', {})
                self._weather_hist = data.get('weather_hist', {})
                self._gym_team = data.get('gym_team', {})
                self._gym_name = data.get('gym_name', {})
                self._gym_desc = data.get('gym_desc', {})
                self._gym_image = data.get('gym_image', {})
                self._reward = data.get('reward', {})

                log.debug("Cache loaded successfully.")
        except Exception as e:
            log.error("There was an error attempting to load the cache. The "
                      "old cache will be overwritten.")
            log.error("{}: {}".format(type(e).__name__, e))

    def _save(self):
        """ Export the data to a more permanent location. """
        log.debug("Writing cache to file...")
        data = {
            'pokemon_hist': self._pokemon_hist,
            'pokestop_hist': self._pokestop_hist,
            'gym_team': self._gym_team,
            'gym_info': self._gym_info,
            'egg_hist': self._egg_hist,
            'raid_hist': self._raid_hist,
            'weather_hist': self._weather_hist,
            'gym_name': self._gym_name,
            'gym_desc': self._gym_desc,
            'gym_image': self._gym_image,
            'reward': self._reward
        }
        log.debug(self._pokestop_hist)
        log.debug("SAVED: {}".format(data))
        try:
            with portalocker.Lock(self._file, timeout=5, mode="wb+") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            log.error("Encountered error while saving cache: "
                      + "{}: {}".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
