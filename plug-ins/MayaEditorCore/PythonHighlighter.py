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
"""Syntax highlighter for Python source code."""
from typing import Any, Dict, List, Tuple

import maya.cmds as cmds
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextBlockUserData,
    QTextCharFormat,
)


def _create_format(style_colour: str, style: str = "") -> QTextCharFormat:
    """Create a QTextCharFormat from a named colour string.

    Parameters
    ----------
    style_colour : str
        Named colour string (e.g. ``"darkGray"``).
    style : str
        Optional style flags; ``"bold"`` and/or ``"italic"``.

    Returns
    -------
    QTextCharFormat
        The configured text format.
    """
    colour = QColor()
    colour.setNamedColor(style_colour)
    new_format = QTextCharFormat()
    new_format.setForeground(QBrush(colour))
    if "bold" in style:
        new_format.setFontWeight(QFont.Bold)
    if "italic" in style:
        new_format.setFontItalic(True)
    return new_format


def _create_format_rgb(style_colour: QColor, style: str = "") -> QTextCharFormat:
    """Create a QTextCharFormat from a QColor.

    Parameters
    ----------
    style_colour : QColor
        Colour for the text foreground.
    style : str
        Optional style flags; ``"bold"`` and/or ``"italic"``.

    Returns
    -------
    QTextCharFormat
        The configured text format.
    """
    new_format = QTextCharFormat()
    new_format.setForeground(QBrush(style_colour))
    if "bold" in style:
        new_format.setFontWeight(QFont.Bold)
    if "italic" in style:
        new_format.setFontItalic(True)
    return new_format


class PythonHighlighter(QSyntaxHighlighter):
    """QSyntaxHighlighter for Python with keyword, operator, string and comment rules."""

    keywords: List[str] = [
        "and", "assert", "break", "class", "continue", "def",
        "del", "elif", "else", "except", "exec", "finally", "for", "from",
        "global", "if", "import", "in", "is", "lambda", "not", "or", "pass",
        "print", "raise", "return", "try", "while", "yield", "None",
        "True", "False",
    ]

    operators: List[str] = [
        "=",
        "==", "!=", "<", "<=", "[^>]>", ">=",
        "\\+", "-", "\\*", "/", "//", "\\%", "\\*\\*",
        "\\+=", "-=", "\\*=", "/=", "\\%=",
        "\\^", "\\|", "\\&", "\\~", "[^>]>>", "<<",
    ]

    braces: List[str] = ["\\{", "\\}", "\\(", "\\)", "\\[", "\\]"]

    mayaCmds: List[str] = cmds.help("[a-z]*", list=True, lng="Python")

    def __init__(self, parent: Any = None) -> None:
        """Initialise the highlighter with colour rules.

        Parameters
        ----------
        parent : object or None
            Parent object for the QSyntaxHighlighter.
        """
        super().__init__(parent)
        self.styles: Dict[str, QTextCharFormat] = {
            "keyword": _create_format_rgb(QColor(255, 166, 87)),
            "operator": _create_format_rgb(QColor(255, 166, 87)),
            "brace": _create_format("darkGray"),
            "defclass": _create_format_rgb(QColor(255, 166, 87)),
            "deffunc": _create_format_rgb(QColor(121, 192, 234)),
            "string": _create_format_rgb(QColor(165, 214, 255)),
            "string2": _create_format_rgb(QColor(165, 214, 255)),
            "comment": _create_format_rgb(QColor("Gray")),
            "self": _create_format_rgb(QColor(121, 192, 255)),
            "numbers": _create_format("GhostWhite"),
            "maya": _create_format("SpringGreen"),
        }
        self.tri_single: Tuple[QRegularExpression, int, QTextCharFormat] = (
            QRegularExpression("'''"), 1, self.styles["string2"],
        )
        self.tri_double: Tuple[QRegularExpression, int, QTextCharFormat] = (
            QRegularExpression('"""'), 2, self.styles["string2"],
        )

        rules: List[Tuple[str, int, QTextCharFormat]] = []
        rules += [
            (r"\b%s\b" % w, 0, self.styles["keyword"])
            for w in PythonHighlighter.keywords
        ]
        rules += [
            (r"%s" % o, 0, self.styles["operator"]) for o in PythonHighlighter.operators
        ]
        rules += [
            (r"%s" % b, 0, self.styles["brace"]) for b in PythonHighlighter.braces
        ]
        rules += [
            (r"\bself\b", 0, self.styles["self"]),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles["string"]),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles["string"]),
            (r"\bdef\b\s*(\w+)", 1, self.styles["deffunc"]),
            (r"\bclass\b\s*(\w+)", 1, self.styles["defclass"]),
            (r"#[^\n]*", 0, self.styles["comment"]),
            (r"\b[+-]?[0-9]+[lL]?\b", 0, self.styles["numbers"]),
            (r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b", 0, self.styles["numbers"]),
            (
                r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b",
                0,
                self.styles["numbers"],
            ),
        ]
        self.rules: List[Tuple[QRegularExpression, int, QTextCharFormat]] = [
            (QRegularExpression(pat), index, fmt) for (pat, index, fmt) in rules
        ]

    def highlightBlock(self, textBlock: str) -> None:
        """Apply syntax highlighting to the given block of text.

        Parameters
        ----------
        textBlock : str
            The text block to highlight.
        """
        for expr, nth, syFormat in self.rules:
            match = expr.match(textBlock)
            while match.hasMatch():
                index = match.capturedStart(nth)
                length = len(match.captured(nth))
                self.setFormat(index, length, syFormat)
                match = expr.match(textBlock, index + length)
        self.setCurrentBlockState(0)
        in_multiline = self.match_multiline(textBlock, *self.tri_single)
        if not in_multiline:
            self.match_multiline(textBlock, *self.tri_double)

    def match_multiline(
        self,
        textBlock: str,
        delimiter: QRegularExpression,
        in_state: int,
        style: QTextCharFormat,
    ) -> bool:
        """Apply highlighting for multi-line string delimiters.

        Parameters
        ----------
        textBlock : str
            Current text block.
        delimiter : QRegularExpression
            The delimiter pattern.
        in_state : int
            Block state value representing being inside a multi-line string.
        style : QTextCharFormat
            Format to apply to the multi-line string content.

        Returns
        -------
        bool
            True if the block ends inside a multi-line string.
        """
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
        return bool(self.currentBlockState() == in_state)