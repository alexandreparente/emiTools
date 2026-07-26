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


def format_cpf_logic(cpf_string) -> str:
    cleaned_string = "".join(filter(str.isdigit, str(cpf_string)))
    if len(cleaned_string) != 11:
        raise ValueError(
            tr("Invalid number. Please provide an 11-digit numeric string.")
        )
    return f"{cleaned_string[:3]}.{cleaned_string[3:6]}.{cleaned_string[6:9]}-{cleaned_string[9:]}"


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def format_cpf(cpf_string, feature, parent):
    """
    Returns a formatted string for CPF (Brazilian individual taxpayer ID).
    <br><br>Note: This function does not verify the validity of the provided number.
    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">format_cpf</b> (<i style="color:#bf0c0c;">string</i>)</p>
    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: A numeric string containing 11 digits.</p>
    <h4>Example:</h4>
    <ul>
      <li> format_cpf('00000000000') -> 000.000.000-00</li>
      <li> format_cpf('BR000,000,000-00') -> 000.000.000-00</li>
    </ul>
    """
    return format_cpf_logic(cpf_string)
