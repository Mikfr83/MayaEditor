# Copyright (C) 2022  Jonathan Macey
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Custom Highlighter for Python.

This will be attached to the editor to do code syntax highlighting, modified from
the Qt Editor example and other sources. 
"""

from typing import Any, Dict

import maya.cmds as cmds
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import *
from PySide6.QtWidgets import *


def _create_format(style_colour: str, style: str = "") -> QTextCharFormat:
    colour = QColor()
    colour.setNamedColor(style_colour)

    new_format = QTextCharFormat()
    new_format.setForeground(QBrush(colour))
    if "bold" in style:
        new_format.setFontWeight(QFont.Bold)  # type: ignore
    if "italic" in style:
        new_format.setFontItalic(True)

    return new_format


def _create_format_rgb(style_colour: QColor, style: str = "") -> QTextCharFormat:
    new_format = QTextCharFormat()
    new_format.setForeground(QBrush(style_colour))
    if "bold" in style:
        new_format.setFontWeight(QFont.Bold)  # type: ignore
    if "italic" in style:
        new_format.setFontItalic(True)

    return new_format


class MelHighlighter(QSyntaxHighlighter):
    # fmt: off
    # Mel keywords
    keywords = ["and", "as", "case", "catch", "continue", "do", "else", "exit", "false", "for" ,"from" ,"if", "in", "local", "not", "of", "off", "on", "or", "random", "return", "then", "throw", "to", "true", "try", "when", "where", "while", "with", "vector","string", "float", "int", "array","proc","global" ]

    # Mel operators
#    ! ( ) . ; [ \ ] ` + &lt; = &gt
    operators = [
        "=",
        # Comparison
        "==","!=","<","<=","[^>]>",">=",
        # Arithmetic
        "\+","-","\*","/","//", "\%","\*\*",
        # In-place 
        "\+=","-=","\*=","/=","\%=",
        # Bitwise
        "\^", "\|","\&","\~","[^>]>>","<<"]

    # Python braces
    braces = ["\{","\}","\(","\)","\[","\]"] 
    # fmt: on

    mayaCmds = cmds.help("[a-z]*", list=True)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.styles = {
            "keyword": _create_format_rgb(QColor(255, 166, 87)),
            "operator": _create_format_rgb(QColor(255, 166, 87)),
            "brace": _create_format("darkGray"),
            "deffunc": _create_format_rgb(QColor(121, 192, 234)),
            "string": _create_format_rgb(QColor(165, 214, 255)),
            "string2": _create_format_rgb(QColor(165, 214, 255)),  # "yellow"),
            "comment": _create_format_rgb("Gray"),
            "self": _create_format_rgb(QColor(121, 192, 255)),
            "numbers": _create_format("GhostWhite"),
            "maya": _create_format("SpringGreen"),
        }
        self.tri_single = (QRegularExpression("'''"), 1, self.styles["string2"])
        self.tri_double = (QRegularExpression('"""'), 2, self.styles["string2"])

        rules = []
        # Keyword, operator, and brace rules
        rules += [
            (r"\b%s\b" % w, 0, self.styles["keyword"]) for w in MelHighlighter.keywords
        ]

        rules += [
            (r"%s" % o, 0, self.styles["operator"]) for o in MelHighlighter.operators
        ]
        rules += [(r"%s" % b, 0, self.styles["brace"]) for b in MelHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r"\bself\b", 0, self.styles["self"]),
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles["string"]),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles["string"]),
            # 'proc' followed by an identifier
            (r"\bproc\b\s*(\w+)", 1, self.styles["deffunc"]),
            # From '//' until a newline
            (r"//[^\n]*", 0, self.styles["comment"]),
            # Numeric literals
            (r"\b[+-]?[0-9]+[lL]?\b", 0, self.styles["numbers"]),
            (r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b", 0, self.styles["numbers"]),
            (
                r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b",
                0,
                self.styles["numbers"],
            ),
        ]

        # Build a QRegularExpression for each pattern
        self.rules = [(QRegularExpression(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, textBlock: str) -> None:
        # Do other syntax formatting
        for expr, nth, syFormat in self.rules:
            match = expr.match(textBlock)
            while match.hasMatch():
                index = match.capturedStart(nth)
                length = len(match.captured(nth))
                self.setFormat(index, length, syFormat)
                match = expr.match(textBlock, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(textBlock, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(textBlock, *self.tri_double)

    def match_multiline(self, textBlock: str, delimiter: QRegularExpression, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            match = delimiter.match(textBlock)
            if not match.hasMatch():
                start = -1
                add = 0
            else:
                start = match.capturedStart()
                add = match.capturedLength()

        while start >= 0:
            end_match = delimiter.match(textBlock, start + add)
            if end_match.hasMatch():
                end = end_match.capturedStart()
                length = end - start + add + end_match.capturedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(textBlock) - start + add
            self.setFormat(start, length, style)
            next_match = delimiter.match(textBlock, start + length)
            if not next_match.hasMatch():
                break
            start = next_match.capturedStart()
            add = next_match.capturedLength()

        if self.currentBlockState() == in_state:
            return True
        return False
