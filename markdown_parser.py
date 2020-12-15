#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import dataclasses as dcs
import datetime as dt
import re
from typing import Dict, List, Tuple, Union

from tty7tyil_python import normalize_string as ns
from tty7tyil_python import tree


class MD_Data:
    __REGEX_TOC_HEADER = re.compile(
        r'^(#{1,6}) (.+)$',
        flags=re.MULTILINE,
    )

    @dcs.dataclass
    class TOC_Header_Data:
        level_in_file: int
        content: str
        serial: int

    def __init__(self, md_file_content: str):
        self.file_header: Dict[
            str, Union[dt.datetime, Tuple[str, ...], None]
        ] = MD_Data.extract_file_header(md_file_content)
        self.toc_tree: tree.Tree[MD_Data.TOC_Header_Data] = MD_Data.extract_toc(md_file_content)
        self.content = md_file_content

    @staticmethod
    def extract_file_header(md_file_content: str):
        pass

    @staticmethod
    def extract_toc(md_file_content: str) -> tree.Tree[MD_Data.TOC_Header_Data]:
        raw_toc_list = MD_Data.__REGEX_TOC_HEADER.findall(md_file_content)
        toc_header_data_list = []

        serial_dict: Dict[str, int] = {}
        # initialize the serial to 0 for every toc content
        for e in raw_toc_list:
            serial_dict[e[1]] = 0
        # fill the list while counting serial
        for e in raw_toc_list:
            toc_header_data_list.append(MD_Data.TOC_Header_Data(len(e[0]), e[1], serial_dict[e[1]]))
            serial_dict[e[1]] += 1

        return MD_Data.__fill_toc_tree(
            tree.Tree(MD_Data.TOC_Header_Data(0, 'Table of Contents', 0)),
            toc_header_data_list,
        )[0]

    @staticmethod
    def __fill_toc_tree(
        toc_tree: tree.Tree[MD_Data.TOC_Header_Data],
        toc_header_data_list: List[MD_Data.TOC_Header_Data],
        /,
        start_index: int = 0,
    ) -> Tuple[tree.Tree[MD_Data.TOC_Header_Data], int]:
        toc_level = toc_header_data_list[start_index].level_in_file
        i = start_index
        while True:
            if i == len(toc_header_data_list):
                return toc_tree, i
            elif toc_header_data_list[i].level_in_file == toc_level:
                toc_tree.branches.append(tree.Tree(toc_header_data_list[i]))
                i += 1
            elif toc_level < toc_header_data_list[i].level_in_file:
                sub_tree, i = MD_Data.__fill_toc_tree(
                    toc_tree.branches[-1],
                    toc_header_data_list,
                    i
                )
                toc_tree.branches[-1] = sub_tree
            else:
                return toc_tree, i

    def titles(self) -> Tuple[str, ...]:
        return tuple(e.data.content for e in self.toc_tree.branches)


TOC_BEGIN_COMMENT = '<!-- GMT TOC BEGIN -->'
TOC_END_COMMENT = '<!-- GMT TOC END -->'
EXIST_TOC_REGEX = re.compile(
    # This regex will match solid consecutive lines (aka no blank lines in
    # the middle) begin with `TOC_BEGIN_COMMENT`, end with `TOC_END_COMMENT`,
    # surrounded by at least one blank lines before and after.
    #
    # Therefore a TOC placeholder can be placed in the file beforehand, other
    # than let this script insert TOC right below the first level header.
    r'(?<=\n\n){tbc}\n(.+\n)*?{tec}(?=\n\n)'.format(
        tbc = repr(TOC_BEGIN_COMMENT)[1:-1],
        tec = repr(TOC_END_COMMENT)[1:-1],
    )
)

def gen_md_toc(
    toc_tree: tree.Tree[MD_Data.TOC_Header_Data],
    /,
    *,
    include_begin_end_comment: bool = False,
    bullet_char: str = '-',
    indentation: int = 2,
) -> str:
    toc: List[str] = []
    for b in toc_tree.branches:
        toc.append(
            tree.Tree.format_as_string(
                b,
                content_parser=lambda e: '[{content}](#{anchor}{serial})'.format(
                    content=e.content,
                    anchor=ns.normalize_string(e.content),
                    serial=('-{}'.format(e.serial) if 0 < e.serial else ''),
                ),
                trunk_char=' ',
                branch_char=bullet_char,
                branch_leading_char=' ',
                indentation=indentation,
            )
        )
    if include_begin_end_comment:
        toc.insert(0, '{}\n'.format(TOC_BEGIN_COMMENT))
        toc.append(TOC_END_COMMENT)
    return ''.join(toc).strip('\n')
