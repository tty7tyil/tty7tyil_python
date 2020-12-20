#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Tuple

# reference: https://gist.github.com/asabaylus/3071099
# 1. to lower case (1)
# 2. only keep [` `, `-`, `_`, word, CJK word, ], remove all others (including CJK punctuation) (2)
# 3. replace all space ` ` with `-` (3)

VALID_CHAR: Tuple[str, ...] = (
    # Word `\w` includes underscore `_`.  (`\w` == `[a-zA-Z0-9_]`)
    # Unicode range 4E00-9FFF is for 'CJK Unified Ideographs' Unicode Block
    r'\w',
    r'\u4e00-\u9fff',
    r' ',
    r'\-',
)

REGEX_CHAR_TO_REMOVE = re.compile(r'[^{}]'.format(''.join(VALID_CHAR)))


def normalize_string(raw_string: str) -> str:
    # steps:
    # 1. replace space (3)
    # 2. remove others (2)
    # 3. to lower case (1)
    string = raw_string.replace(' ', '-')
    string = REGEX_CHAR_TO_REMOVE.sub('', string)
    string = string.lower()
    return string


def main():
    pass


if (__name__ == '__main__'):
    main()
