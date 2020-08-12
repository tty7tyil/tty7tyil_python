#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple
import fake_useragent as fua
import random
import requests
import time


class Crawler_Requests_Session(object):
    def __init__(
        self,
        /,
        user_agent: str = '',
        *,
        proxies_list: List[Dict[str, str]] = [{'http': '', 'https': ''}],
        sleep_interval_range: Tuple[float, float] = (0.5, 2.0),
    ):
        self._user_agent = user_agent
        self._proxies_list = proxies_list
        self._sleep_interval_range = sleep_interval_range
        self.__fua = fua.UserAgent()
        self.refresh_identity()

    def refresh_identity(self):
        self.__session = requests.Session()
        self.__session.proxies.update(random.choice(self._proxies_list))
        if self._user_agent == '':
            self._user_agent == self.__fua.random
        self.__session.headers.update({'User-Agent': self._user_agent})

    def get(self, *args, **kwargs):
        time.sleep(random.uniform(*self._sleep_interval_range))
        return self.__session.get(*args, **kwargs)
