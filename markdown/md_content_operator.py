#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from typing import List

from tty7tyil_python import tree
from tty7tyil_python.markdown import md_structure_data as mdsd
from tty7tyil_python.string_et_output import normalize_string as ns

TOC_BEGIN_COMMENT = '<!-- GMT TOC BEGIN -->'
TOC_END_COMMENT = '<!-- GMT TOC END -->'


def gen_md_toc(
    md_file_content: str,
    /,
    *,
    include_begin_end_comment: bool = False,
    bullet_char: str = '-',
    indentation: int = 2,
) -> str:
    toc_tree = mdsd.MD_Structure_Data(md_file_content).toc_tree
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


__REGEX_EXISTING_TOC = re.compile(
    # This regex will match solid consecutive lines (aka no blank lines in
    # the middle) begin with `TOC_BEGIN_COMMENT`, end with `TOC_END_COMMENT`,
    # surrounded by at least one blank lines before and after.
    #
    # Therefore a TOC placeholder can be placed in the file beforehand, other
    # than let this script insert TOC right below the first level header.
    r'(?<=\n\n){tbc}\n(.+\n)*?{tec}(?=\n\n)'.format(
        tbc=repr(TOC_BEGIN_COMMENT)[1:-1],
        tec=repr(TOC_END_COMMENT)[1:-1],
    )
)
__REGEX_FIRST_LEVEL_HEADER = re.compile(
    r'^(?P<flh># .+)$',
    flags=re.MULTILINE,
)


def write_toc_to_md_file(
    file_path: str, /, *, given_content_not_path: bool = False, write_to_file: bool = True
) -> str:
    if given_content_not_path:
        file_content = file_path
        write_to_file = False
    else:
        with open(file_path, mode='rt', encoding='utf-8') as f:
            file_content = f.read()

    toc = gen_md_toc(file_content, include_begin_end_comment=True)
    # Read literal `text\1{a new line}test` into python will get:
    # `text\\1\ntest` (`repr` * 1).  To pass this to the `re` module,
    # we need to escape it again (`repr` * 2), produce `text\\\\1\\ntest`.
    if __REGEX_EXISTING_TOC.search(file_content) is not None:
        file_content = __REGEX_EXISTING_TOC.sub(repr(toc)[1:-1], file_content)
    else:
        file_content = __REGEX_FIRST_LEVEL_HEADER.sub(
            r''.join(
                (
                    r'\g<flh>\n',
                    r'\n',
                    repr(toc)[1:-1],
                    r'\n',
                    r'\n---',
                )
            ),
            file_content
        )

    if write_to_file:
        with open(file_path, mode='wt', encoding='utf-8', newline='\n') as f:
            f.write(file_content)

    return file_content
