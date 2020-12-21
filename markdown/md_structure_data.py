#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import dataclasses as dcs
import datetime as dt
import re
from typing import Dict, List, Tuple, Union

from tty7tyil_python import tree


class MD_Structure_Data:
    # TODO
    # - [ ] implement key-like access on toc_tree just like dict (problem: but the data as key is
    # not necessary unique like in dict)
    # - [ ] implement `__str__` method

    @dcs.dataclass
    class TOC_Header_Data:
        level_in_file: int
        content: str
        serial: int

    def __init__(self, md_file_content: str, /):
        self.file_header: Dict[
            str, Union[dt.datetime, Tuple[str, ...], None]
        ] = MD_Structure_Data.extract_file_header(md_file_content)
        self.toc_tree: tree.Tree[
            MD_Structure_Data.TOC_Header_Data
        ] = MD_Structure_Data.extract_toc(md_file_content)

    FILE_HEADER_BEGIN_COMMENT = '<!-- metadata header ---'
    FILE_HEADER_END_COMMENT = '---- metadata header -->'
    __REGEX_FILE_HEADER = re.compile(
        r'^{fhbc}\n(.+\n)*?{fhec}$'.format(
            fhbc=repr(FILE_HEADER_BEGIN_COMMENT)[1:-1],
            fhec=repr(FILE_HEADER_END_COMMENT)[1:-1],
        ),
        flags=re.MULTILINE,
    )
    __REGEX_FILE_HEADER_DATA_PAIR = re.compile(
        r' *(.+?) *: *(.*?) *$',
        flags=re.MULTILINE,
    )

    @staticmethod
    def extract_file_header(
        md_file_content: str,
    ) -> Dict[str, Union[dt.datetime, Tuple[str, ...], None]]:
        if (m := MD_Structure_Data.__REGEX_FILE_HEADER.search(md_file_content)) is not None:
            raw_data_pair_list = MD_Structure_Data.__REGEX_FILE_HEADER_DATA_PAIR.findall(
                md_file_content[m.start():m.end()]
            )
            data_pair_dict: Dict[str, Union[dt.datetime, Tuple[str, ...], None]] = dict()
            for p in raw_data_pair_list:
                if 'time' in p[0]:
                    # the datetime string format should be `1970-01-01 00:00:00 Z`
                    # !!! AND ALWAYS IN UTC !!!
                    if p[1][-1] == 'Z':
                        # datetime string
                        data_pair_dict[p[0]] = dt.datetime(
                            int(p[1][0:4]),
                            int(p[1][5:7]),
                            int(p[1][8:10]),
                            int(p[1][11:13]),
                            int(p[1][14:16]),
                            int(p[1][17:19]),
                            tzinfo=dt.timezone.utc,
                        )
                    else:
                        raise ValueError('date time string not presented in utc')
                elif ',' in p[1]:
                    # string list, separated by comma ','
                    data_pair_dict[p[0]] = tuple(
                        e for e in (
                            re.strip(' ') for re in p[1].split(',')
                        ) if e != ''
                    )
                elif p[1] == '':
                    # empty value
                    data_pair_dict[p[0]] = None
                else:
                    raise ValueError(
                        'file header data cannot be interpret as datetime string or string list'
                    )
            return data_pair_dict
        else:
            return dict()

    __REGEX_TOC_HEADER = re.compile(
        r'^(#{1,6}) (.+)$',
        flags=re.MULTILINE,
    )

    @staticmethod
    def extract_toc(md_file_content: str) -> tree.Tree[MD_Structure_Data.TOC_Header_Data]:
        raw_toc_list = MD_Structure_Data.__REGEX_TOC_HEADER.findall(md_file_content)
        toc_header_data_list = []

        serial_dict: Dict[str, int] = {}
        # initialize the serial to 0 for every toc content
        for e in raw_toc_list:
            serial_dict[e[1]] = 0
        # fill the list while counting serial
        for e in raw_toc_list:
            toc_header_data_list.append(
                MD_Structure_Data.TOC_Header_Data(len(e[0]), e[1], serial_dict[e[1]])
            )
            serial_dict[e[1]] += 1

        return MD_Structure_Data.__fill_toc_tree(
            tree.Tree(MD_Structure_Data.TOC_Header_Data(0, 'Table of Contents', 0)),
            toc_header_data_list,
        )[0]

    @staticmethod
    def __fill_toc_tree(
        toc_tree: tree.Tree[MD_Structure_Data.TOC_Header_Data],
        toc_header_data_list: List[MD_Structure_Data.TOC_Header_Data],
        /,
        start_index: int = 0,
    ) -> Tuple[tree.Tree[MD_Structure_Data.TOC_Header_Data], int]:
        toc_level = toc_header_data_list[start_index].level_in_file
        i = start_index
        while True:
            if i == len(toc_header_data_list):
                return toc_tree, i
            elif toc_header_data_list[i].level_in_file == toc_level:
                toc_tree.branches.append(tree.Tree(toc_header_data_list[i]))
                i += 1
            elif toc_level < toc_header_data_list[i].level_in_file:
                sub_tree, i = MD_Structure_Data.__fill_toc_tree(
                    toc_tree.branches[-1],
                    toc_header_data_list,
                    i
                )
                toc_tree.branches[-1] = sub_tree
            else:
                return toc_tree, i

    def titles(self) -> Tuple[str, ...]:
        return tuple(e.data.content for e in self.toc_tree.branches)
