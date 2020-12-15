#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Callable, Generic, List, Sequence, TypeVar

TreeDT = TypeVar('TreeDT')


class Tree(Generic[TreeDT]):
    def __init__(self, data: TreeDT, branches: Sequence[Tree[TreeDT]] = tuple()):
        self.data = data
        self.branches: List[Tree[TreeDT]] = list(branches)

    def __str__(self) -> str:
        return Tree.format_as_string(self)

    @staticmethod
    def format_as_string(
        tree: Tree[TreeDT],
        /,
        indentation_prefix: str = '',
        last: bool = True,
        *,
        content_parser: Callable[[TreeDT], str] = str,
        trunk_char: str = '|',
        branch_char: str = '+',
        branch_leading_char: str = '-',
        indentation_char: str = ' ',
        indentation: int = 3,
    ) -> str:
        output = '{prefix}{branch}{leading} {content}\n'.format(
            prefix=indentation_prefix,
            branch=branch_char,
            leading=branch_leading_char * (indentation - 2),
            content=content_parser(tree.data),
        )
        branches_content_list = []
        for i in range(len(tree.branches)):
            branches_content_list.append(
                Tree.format_as_string(
                    tree.branches[i],
                    (
                        indentation_prefix
                        + (
                            (indentation_char * indentation)
                            if last is True
                            else (trunk_char + indentation_char * (indentation - 1))
                        )
                    ),
                    True if i == len(tree.branches) - 1 else False,
                    content_parser=content_parser,
                    trunk_char=trunk_char,
                    branch_char=branch_char,
                    branch_leading_char=branch_leading_char,
                    indentation_char=indentation_char,
                    indentation=indentation,
                )
            )

        return ''.join((output, *branches_content_list))
