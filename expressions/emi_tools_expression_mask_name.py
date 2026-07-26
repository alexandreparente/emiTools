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


def mask_name_logic(full_name) -> str:
    parts = str(full_name).split()
    if len(parts) < 3:
        return str(full_name)
    middle = ["*" * len(p) for p in parts[1:-1]]
    return parts[0] + " " + " ".join(middle) + " " + parts[-1]


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def mask_name(full_name, feature, parent):
    """
    Masks the middle part of a name by hiding the internal parts, leaving the first and last names visible.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">mask_name</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: A string containing the full name to be masked.</p>

    <h4>Returns</h4>
    <ul>
      <li>A string with the masked middle part of the name, e.g. 'Alexandre ******* Lima'.</li>
    </ul>
    """
    return mask_name_logic(full_name)
