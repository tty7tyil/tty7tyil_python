#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from typing import Set
from typing import Tuple
import math
import numpy
import pandas
import random
import scipy.stats
import uuid


class ID_Library:
    def __init__(self, power: int = None):
        self.uuid4_set: Set[Tuple[str, numpy.float64]] = set()
        self.len16_set: Set[Tuple[str, numpy.float64]] = set()
        self.len12_set: Set[Tuple[str, numpy.float64]] = set()
        self.len8_set: Set[Tuple[str, numpy.float64]] = set()
        if power is not None:
            self.populate(power)

    def populate(
        self,
        power: int = 8,
        leading_char_lower_limit: str = '1',  # inclusive
        leading_char_upper_limit: str = 'F',  # inclusive
        show_progress: bool = True,
    ):
        uuid4_list: List[Tuple[str, numpy.float64]] = []
        len16_list: List[Tuple[str, numpy.float64]] = []
        len12_list: List[Tuple[str, numpy.float64]] = []
        len8_list: List[Tuple[str, numpy.float64]] = []

        lcll = (int(leading_char_lower_limit, 16) * 0x_1000_0000_0000_0000_0000_0000_0000_0000) - 1
        lcul = (int(leading_char_upper_limit, 16) + 1) * 0x_1000_0000_0000_0000_0000_0000_0000_0000

        for i in range(2 ** power):
            uuid4 = uuid.uuid4()
            if lcll < uuid4.int < lcul:
                uuid4_list.append(
                    (
                        str(uuid4).upper(),
                        scipy.stats.entropy(pandas.Series(c for c in uuid4.hex).value_counts()),
                    )
                )
                len16_list.append(
                    (
                        value := uuid4.hex[:16].upper(),
                        scipy.stats.entropy(pandas.Series(c for c in value).value_counts()),
                    )
                )
                len12_list.append(
                    (
                        value := uuid4.hex[:12].upper(),
                        scipy.stats.entropy(pandas.Series(c for c in value).value_counts()),
                    )
                )
                len8_list.append(
                    (
                        value := uuid4.hex[:8].upper(),
                        scipy.stats.entropy(pandas.Series(c for c in value).value_counts()),
                    )
                )

            if show_progress:
                total = 2 ** power
                percent = (i + 1) / total
                bar_len = 50
                left_bar = math.floor(bar_len * percent)
                print(
                    'PROGRESS: {:_>{}} / {}  [{}{}{}] {: >5}%'.format(
                        i + 1, len(str(total)), total,
                        '=' * left_bar,
                        '>' if left_bar < bar_len else '',
                        ' ' * (bar_len - left_bar - 1),
                        int(percent * 100 * 10) / 10,
                    ),
                    end='',
                )
                print('\r', end='')

        uuid4_set = self.__class__.__top_entropy(set(uuid4_list))
        len16_set = self.__class__.__top_entropy(set(len16_list))
        len12_set = self.__class__.__top_entropy(set(len12_list))
        len8_set = self.__class__.__top_entropy(set(len8_list))
        uuid4_set, len16_set, len12_set, len8_set = self.__class__.__trim(
            uuid4_set, len16_set, len12_set, len8_set
        )

        self.uuid4_set |= uuid4_set
        self.len16_set |= len16_set
        self.len12_set |= len12_set
        self.len8_set |= len8_set

        self.uuid4_set = self.__class__.__top_entropy(self.uuid4_set)
        self.len16_set = self.__class__.__top_entropy(self.len16_set)
        self.len12_set = self.__class__.__top_entropy(self.len12_set)
        self.len8_set = self.__class__.__top_entropy(self.len8_set)

    @staticmethod
    def __top_entropy(
        value_set: Set[Tuple[str, numpy.float64]], at_least: int = 10
    ) -> Set[Tuple[str, numpy.float64]]:
        value_list = list(value_set)
        value_list.sort(key=lambda e: e[1], reverse=True)
        for i in range(1, len(value_list)):
            if (value_list[i][1] < value_list[i - 1][1]) and (at_least <= i):
                return set(value_list[:i])
        return value_set

    @staticmethod
    def __trim(uuid4_set, len16_set, len12_set, len8_set):
        for e in uuid4_set:
            test = e[0].replace('-', '')[:16]
            if test in len16_set:
                len16_set.remove(test)
                len12_set.remove(test[:12])
                len8_set.remove(test[:8])
        for e in len16_set:
            test = e[0][:12]
            if test in len12_set:
                len12_set.remove(test)
                len8_set.remove(test[:8])
        for e in len12_set:
            test = e[0][:8]
            if test in len8_set:
                len8_set.remove(test)
        return uuid4_set, len16_set, len12_set, len8_set

    def uuid4(self, k: int = 1) -> str:
        return tuple(e[0] for e in random.choices(tuple(self.uuid4_set), k=k))

    def len16(self, k: int = 1) -> str:
        return tuple(e[0] for e in random.choices(tuple(self.len16_set), k=k))

    def len12(self, k: int = 1) -> str:
        return tuple(e[0] for e in random.choices(tuple(self.len12_set), k=k))

    def len8(self, k: int = 1) -> str:
        return tuple(e[0] for e in random.choices(tuple(self.len8_set), k=k))

    def __repr__(self) -> str:
        (uuid4_list := list(self.uuid4_set)).sort(key=lambda e: e[1], reverse=True)
        (len16_list := list(self.len16_set)).sort(key=lambda e: e[1], reverse=True)
        (len12_list := list(self.len12_set)).sort(key=lambda e: e[1], reverse=True)
        (len8_list := list(self.len8_set)).sort(key=lambda e: e[1], reverse=True)
        max_len = max(len(uuid4_list), len(len16_list), len(len12_list), len(len8_list))
        return '\n'.join(
            (
                '<{} object at 0x{:X}>'.format(type(self), id(self)),
                'uuid4  : {:_>{}};  entropy in [{}, {}]'.format(
                    len(uuid4_list), len(str(max_len)), uuid4_list[0][1], uuid4_list[-1][1]
                ),
                'len16  : {:_>{}};  entropy in [{}, {}]'.format(
                    len(len16_list), len(str(max_len)), len16_list[0][1], len16_list[-1][1]
                ),
                'len12  : {:_>{}};  entropy in [{}, {}]'.format(
                    len(len12_list), len(str(max_len)), len12_list[0][1], len12_list[-1][1]
                ),
                'len8   : {:_>{}};  entropy in [{}, {}]'.format(
                    len(len8_list), len(str(max_len)), len8_list[0][1], len8_list[-1][1]
                ),
            )
        )


# max entropy record for
#     uuid4: 2.756237217747139      (2 in 2**20)
#     len16: 2.772588722239781      (maxed out)
#     len12: 2.484906649788001      (maxed out)
#     len8 : 2.0794415416798357     (maxed out)
