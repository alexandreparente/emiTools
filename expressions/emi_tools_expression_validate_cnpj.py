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


def validate_cnpj_logic(cnpj_number) -> bool:
    s = "".join(filter(str.isdigit, str(cnpj_number)))
    if len(s) != 14:
        return False
    if s == s[0] * 14:
        return False
    nums = list(map(int, s))
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    dv1 = 11 - (sum(n * w for n, w in zip(nums[:12], w1)) % 11)
    dv1 = 0 if dv1 > 9 else dv1
    dv2 = 11 - (sum(n * w for n, w in zip(nums[:13], w2)) % 11)
    dv2 = 0 if dv2 > 9 else dv2
    return nums[12] == dv1 and nums[13] == dv2


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def validate_cnpj(cnpj_number, feature, parent):
    """
    Returns True if the provided string is a valid Brazilian Corporate Taxpayer Identification Number (CNPJ). Otherwise, returns False.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">validate_cnpj</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: A 14-character text string representing a CNPJ number.</p>

    <h4>Example:</h4>
    <ul>
      <li> validate_cnpj('00.000.000/0000-00') -> True</li>
      <li> validate_cnpj('00.000.000/0000-01') -> False</li>
    </ul>
    """
    return validate_cnpj_logic(cnpj_number)
