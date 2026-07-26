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


def validate_cpf_logic(cpf_number) -> bool:
    s = "".join(filter(str.isdigit, str(cpf_number)))
    if len(s) != 11:
        return False
    # rejects CPFs with all equal digits
    if s == s[0] * 11:
        return False
    nums = list(map(int, s))
    total = sum(a * b for a, b in zip(nums[:9], range(10, 1, -1)))
    dv = (total * 10) % 11
    if dv == 10:
        dv = 0
    if dv != nums[9]:
        return False
    total = sum(a * b for a, b in zip(nums[:10], range(11, 1, -1)))
    dv = (total * 10) % 11
    if dv == 10:
        dv = 0
    return dv == nums[10]


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def validate_cpf(cpf_number, feature, parent):
    """
    Returns True if the provided string is a valid Brazilian Individual Taxpayer Identification Number (CPF). Otherwise, returns False.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">validate_cpf</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: A string containing 11 numeric characters representing a CPF number.</p>

    <h4>Example:</h4>
    <ul>
      <li> validate_cpf('000.000.000-00') -> True</li>
      <li> validate_cpf('000.000.000-01') -> False</li>
    </ul>
    """
    return validate_cpf_logic(cpf_number)
