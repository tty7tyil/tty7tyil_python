#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple
import unicodedata as ucd

# Details about Unicode East Asian Width can be found at:
# [UAX #11: East Asian Width](https://www.unicode.org/reports/tr11/tr11-36.html)


def count_visual_length(
    string: str,
    ambiguous_always_wide: bool = False,
    resolve_as_wide: Tuple[str, ...] = (),
) -> int:
    wide = 'FWA' if ambiguous_always_wide else 'FW'
    visual_length = len(string)
    for c in string:
        t = ucd.east_asian_width(c)
        if (t in wide) or (t in resolve_as_wide):
            visual_length += 1
    return visual_length


def align_to_width(
    string: str,
    fill: str,
    align: str,
    width: int,
    *,
    ambiguous_always_wide: bool = False,
    resolve_as_wide: Tuple[str, ...] = (),
) -> str:
    return '{string:{fill}{align}{width}}'.format(
        fill=fill,
        align=align,
        width=(
            width
            - (
                count_visual_length(
                    string,
                    ambiguous_always_wide,
                    resolve_as_wide,
                )
                - len(string)
            )
        ),
        string=string,
    )
