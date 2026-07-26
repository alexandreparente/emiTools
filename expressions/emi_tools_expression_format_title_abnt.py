# -*- coding: utf-8 -*-

"""
/***************************************************************************
 emiTools
                                 A QGIS plugin
 This plugin compiles tools used by EMI-PB

                              -------------------
        begin                : 2024-10-10
        copyright            : (C) 2024 by Alexandre Parente Lima
        email                : alexandre.parente@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = "Alexandre Parente Lima"
__date__ = "2024-10-10"
__copyright__ = "(C) 2024 by Alexandre Parente Lima"

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

from qgis.utils import qgsfunction

from ._text_formatting import format_capitalization_logic


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def format_title_abnt(text, feature, parent):
    """
    Formats the input text as a title according to the guidelines set by the ABNT (Brazilian Association of Technical Standards). It capitalizes all major words, excluding articles, prepositions, and conjunctions, unless they are the first word of the title.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">format_title_abnt</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: The input text to be formatted.</p>

    <h4>Returns</h4>
    <p><i>str</i>: The formatted text following ABNT title formatting.</p>

    <h4>Example:</h4>
    <pre>
    format_title_abnt('Qgis: Um Sistema de Informação Geográfica livre e aberto.') -> 'QGIS: Um Sistema de Informação Geográfica Livre e Aberto.'
    </pre>
    """
    return format_capitalization_logic(text, force_after_strong_punct=True)
