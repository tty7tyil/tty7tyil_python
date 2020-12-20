#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from typing import Dict, List, Tuple, Union

from tty7tyil_python import tree
from tty7tyil_python.markdown import md_structure_data as mdsd
from tty7tyil_python.string_et_output import normalize_string as ns

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
    toc_tree: tree.Tree[mdsd.MD_Structure_Data.TOC_Header_Data],
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
