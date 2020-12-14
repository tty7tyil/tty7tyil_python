#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Generic, List, Sequence, Tuple, TypeVar

TreeDT = TypeVar('TreeDT')


class Tree(Generic[TreeDT]):
    def __init__(self, data: TreeDT, branches: Sequence[Tree[TreeDT]] = None):
        self.data = data
        self.branches: List[Tree[TreeDT]] = list(branches) if branches is not None else list()

    def __str__(self) -> str:
        return Tree.format_as_string(self)

    @staticmethod
    def format_as_string(tree: Tree, indentation_prefix: str = '', last: bool = True) -> str:
        trunk_char = '|'
        branch_char = '+'
        branch_leading_char = '-'
        indentation_char = ' '
        indentation = 3

        output = '{prefix}{branch}{leading} {content}\n'.format(
            prefix=indentation_prefix,
            branch=branch_char,
            leading=branch_leading_char * (indentation - 2),
            content=str(tree.data),
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
                )
            )

        return ''.join((output, *branches_content_list))


class Frozen_Tree(Tree[TreeDT]):
    # turn list branches into tuple branches, does nothing else
    def __init__(self, tree: Tree[TreeDT]):
        self = tree
        for bi in range(len(self.branches)):
            self.branches[bi] = Frozen_Tree(self.branches[bi])
        self.branches: Tuple[Frozen_Tree[TreeDT], ...] = tuple(self.branches)
