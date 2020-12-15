#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
import re
from typing import Callable, Sequence, Tuple

# how to convert to markdown anchor (reference: https://gist.github.com/asabaylus/3071099)
# 1. to lower case (1)
# 2. only keep [` `, `-`, `_`, word, CJK word, ], remove all others (including CJK punctuation) (2)
# 3. replace all space ` ` with `-` (3)

MD_ANCHOR_VALID_CHAR: Tuple[str, ...] = (
    # Word `\w` includes underscore `_`.  (`\w` == `[a-zA-Z0-9_]`)
    # Unicode range 4E00-9FFF is for 'CJK Unified Ideographs' Unicode Block
    r'\w',
    r'\u4e00-\u9fff',
    r' ',
    r'\-',
)


@enum.unique
class NORMALIZATION_STYLE(enum.Enum):
    MARKDOWN = enum.auto()
    HYPHEN = enum.auto()
    UNDERSCORE = enum.auto()
    DOT = enum.auto()


def normalize_string(
    raw_string: str,
    /,
    style: NORMALIZATION_STYLE = NORMALIZATION_STYLE.MARKDOWN,
    case_converter: Callable[[str], str] = str.lower,
    *,
    valid_char: Sequence[str] = MD_ANCHOR_VALID_CHAR,
) -> str:
    # replace space
    if style in (NORMALIZATION_STYLE.MARKDOWN, NORMALIZATION_STYLE.HYPHEN):
        string = raw_string.replace(' ', '-')
    elif style is NORMALIZATION_STYLE.UNDERSCORE:
        string = raw_string.replace(' ', '_')
    elif style is NORMALIZATION_STYLE.DOT:
        string = raw_string.replace(' ', '.')
    else:  # !!! THIS SHOULD NEVER EVER HAPPEN !!!
        string = raw_string

    # remove others
    if (style is not NORMALIZATION_STYLE.MARKDOWN) and (r'\.' not in valid_char):
        valid_char = list(valid_char)
        valid_char.append(r'\.')
    regex_char_to_remove = re.compile(r'[^{}]'.format(''.join(valid_char)), flags=re.ASCII)
    string = regex_char_to_remove.sub('', string)

    # convert capitalization
    string = case_converter(string)

    return string
