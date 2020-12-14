#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime as dt
import re
from typing import Dict, List, Tuple, Union

from tty7tyil_python import normalize_string as ns
from tty7tyil_python import tree


class MD_Data:
    def __init__(self, md_file_content: str):
        self.file_header: Dict[
            str,
            Union[
                dt.datetime,
                Tuple[str, ...],
                None,
            ]
        ] = MD_Data.extract_file_header(md_file_content)
        self.toc: tree.Tree[str] = MD_Data.extract_toc(md_file_content)

    @staticmethod
    def extract_file_header(md_file_content: str):
        pass

    __REGEX_TOC_HEADER = re.compile(
        r'^(#{1,6}) (.+)$',
        flags=re.MULTILINE,
    )

    @staticmethod
    def extract_toc(md_file_content: str) -> tree.Tree[str]:
        toc_list = MD_Data.__REGEX_TOC_HEADER.findall(md_file_content)
        return MD_Data.__fill_toc_tree(tree.Tree('Table of Contents'), toc_list)[0]

    @staticmethod
    def __fill_toc_tree(
        toc_tree: tree.Tree[str],
        toc_list: List[Tuple[str, str]],
        start_index: int = 0,
    ) -> Tuple[tree.Tree[str], int]:
        toc_level = len(toc_list[start_index][0])
        i = start_index
        while True:
            if i == len(toc_list):
                return toc_tree, i
            elif len(toc_list[i][0]) == toc_level:
                toc_tree.branches.append(tree.Tree(toc_list[i][1]))
                i += 1
            elif toc_level < len(toc_list[i][0]):
                sub_tree, i = MD_Data.__fill_toc_tree(toc_tree.branches[-1], toc_list, i)
                toc_tree.branches[-1] = sub_tree
            else:
                return toc_tree, i
