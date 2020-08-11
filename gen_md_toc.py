#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO
# - [x] write to file
#   - [x] mark the starting and ending line of toc, for toc update
# - [ ] command line interface
#   - [ ] take options and parameters from command line
# - [ ] merge into project 'gen_toc', then complete that project
# - [ ] style
#   - [x] mark keyword-only arguments  
#     [PEP 3102](https://www.python.org/dev/peps/pep-3102/)
#   - [ ] mark positional-only arguments  
#     [PEP 457](https://www.python.org/dev/peps/pep-0457/)  
#     [PEP 570](https://www.python.org/dev/peps/pep-0570/)

from tty7tyil import normalize_string as ns
from typing import Dict, List, Tuple
import re

FIRST_LEVEL_HEADER_REGEX = re.compile(
    r'^(# .+)$',
    flags=re.MULTILINE,
)
HEADER_LEVEL_CONTENT_REGEX = re.compile(
    r'^(#{1,6}) (.+)$',
    flags=re.MULTILINE,
)

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


def headers_to_toc_hierarchy(
    markdown_content: str,
    *,
    include_title: bool = False,
    # -> Tuple[Tuple['toc level', 'header content', 'serial'], ...]
) -> Tuple[Tuple[int, str, int], ...]:
    # : List[Tuple['header level', 'header content']]
    header_level_content_list: List[Tuple[str, str]] = (
        HEADER_LEVEL_CONTENT_REGEX.findall(markdown_content)
    )

    # : Dict['header content', 'serial']
    serial_dict: Dict[str, int] = {}
    for e in header_level_content_list:
        serial_dict[e[1]] = 0

    # : List[Tuple['toc level', 'header content', 'serial']]
    output: List[Tuple[int, str, int]] = []

    for e in header_level_content_list:
        if (include_title):
            output.append((len(e[0]), e[1], serial_dict[e[1]]))
            serial_dict[e[1]] += 1
        else:
            if (e[0] == '#'):
                serial_dict[e[1]] += 1
                continue
            else:
                output.append((len(e[0]) - 1, e[1], serial_dict[e[1]]))
                serial_dict[e[1]] += 1
    return tuple(output)


def generate_markdown_toc(
    markdown_content: str,
    *,
    include_begin_end_comment: bool = False,
    include_title: bool = False,
    # `toc_as_toc_title` only has effect when `include_title` is `False`.
    toc_as_toc_title: bool = True,
    # `toc_string` is the string used for `toc_as_toc_title`.
    toc_string: str = 'Table of Contents',
    indent_cha: str = ' ',
    indent: int = 2,
) -> str:
    toc_entries = headers_to_toc_hierarchy(
        markdown_content,
        include_title = include_title,
    )
    toc: List[str] = []
    if (include_begin_end_comment):
        toc.append(TOC_BEGIN_COMMENT)

    toc_level_offset = 0
    if ((not include_title) and (toc_as_toc_title)):
        toc_level_offset = 1
        toc.append('- {}'.format(toc_string))

    for e in toc_entries:
        toc.append('{indent}- [{content}](#{anchor}{serial})'.format(
            indent = indent_cha * indent * ((e[0] + toc_level_offset) - 1),
            content = e[1],
            anchor = ns.normalize_string(e[1]),
            serial = '-{}'.format(e[2]) if (0 < e[2]) else '',
        ))

    if (include_begin_end_comment):
        toc.append(TOC_END_COMMENT)
    return '\n'.join(toc)


def generate_markdown_file_with_toc(
    file_: str,
    *,
    given_file_content_not_path: bool = False,
    # If `given_file_content_not_path` is `True`,
    # `write_to_file` will be forced to be `False`.
    write_to_file: bool = False,
    # `include_begin_end_comment` in `**kwargs` will be forced to be `True`.
    **kwargs,
) -> str:
    if (given_file_content_not_path):
        write_to_file = False
    kwargs['include_begin_end_comment'] = True

    if (given_file_content_not_path):
        file_content = file_
    else:
        with open(file_, mode='rt', encoding='utf-8') as f:
            file_content = f.read()

    toc = generate_markdown_toc(file_content, **kwargs)

    # Read literal `text\1{a new line}test` into python will get:
    # `text\\1\ntest` (`repr` * 1).  To pass this to the `re` module,
    # we need to escape it again (`repr` * 2), produce `text\\\\1\\ntest`.
    if (EXIST_TOC_REGEX.search(file_content) is not None):
        file_content = EXIST_TOC_REGEX.sub(repr(toc)[1:-1], file_content)
    else:
        file_content = FIRST_LEVEL_HEADER_REGEX.sub(
            r''.join([
                r'\1\n',
                r'\n',
                repr(toc)[1:-1],
                r'\n',
                r'\n---',
            ]),
            file_content
        )

    if (write_to_file):
        with open(
            file_,
            mode='wt', encoding='utf-8', newline='\n',
        ) as f:
            f.write(file_content)

    return file_content


def main():
    pass


if (__name__ == '__main__'):
    main()
