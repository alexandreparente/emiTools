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


def mask_cpf_logic(cpf_number) -> str:
    s = "".join(filter(str.isdigit, str(cpf_number)))
    if len(s) != 11:
        return "Invalid CPF"
    return f"***.{s[3:6]}.{s[6:9]}-**"


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def mask_cpf(cpf_number, feature, parent):
    """
    Masks a CPF number by hiding the first three and last two digits.
    Non-numeric characters are removed before applying the mask.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">mask_cpf</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: A string containing 11 numeric characters representing a CPF number.</p>

    <h4>Example</h4>
    <ul>
      <li>mask_cpf('000.000.000-00') → '***.000.000-**'.</li>
      <li>mask_cpf('000.000.000') → "Invalid CPF" if the provided number does not have exactly 11 digits.</li>
    </ul>
    """
    return mask_cpf_logic(cpf_number)
