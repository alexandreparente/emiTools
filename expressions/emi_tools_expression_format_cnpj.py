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

from ..emi_tools_util import tr


def format_cnpj_logic(cnpj_string) -> str:
    cleaned_string = "".join(filter(str.isdigit, str(cnpj_string)))
    if len(cleaned_string) != 14:
        raise ValueError(
            tr("Invalid number. Pass a numeric string as the input parameter.")
        )
    return f"{cleaned_string[:2]}.{cleaned_string[2:5]}.{cleaned_string[5:8]}/{cleaned_string[8:12]}-{cleaned_string[12:]}"


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def format_cnpj(cnpj_string, feature, parent):
    """
    Returns a formatted string for CNPJ (Brazilian corporate taxpayer ID).
    <br><br>Note: This function does not verify the validity of the provided number.
    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">format_cpf_cnpj</b> (<i style="color:#bf0c0c;">string</i>)</p>
    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: 11 or 14-numeric character string.</p>
    <h4>Example:</h4>
    <ul>
      <li> format_cnpj('00000000000000') -> 00.000.000/0000-00</li>
      <li> format_cnpj('BR00,000,000/0000-00') -> 00.000.000/0000-00</li>
    </ul>
    """
    return format_cnpj_logic(cnpj_string)
