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
        self.__fua = fua.UserAgent()
        self._user_agent = user_agent if user_agent != '' else self.__fua.random
        self._proxies_list = proxies_list
        self._sleep_interval_range = sleep_interval_range
        self.refresh_identity()

    def refresh_identity(self, refresh_user_agent: bool = True):
        self.__session = requests.Session()
        if refresh_user_agent:
            self.__session.headers.update({'User-Agent': self.__fua.random})
        else:
            self.__session.headers.update({'User-Agent': self._user_agent})
        self.__session.proxies.update(random.choice(self._proxies_list))

    def get(self, *args, **kwargs):
        time.sleep(random.uniform(*self._sleep_interval_range))
        return self.__session.get(*args, **kwargs)
