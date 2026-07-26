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
from .emi_tools_expression_format_cnpj import format_cnpj_logic
from .emi_tools_expression_format_cpf import format_cpf_logic


def format_cpf_cnpj_logic(cpf_cnpj_string) -> str:
    cleaned_string = "".join(filter(str.isdigit, str(cpf_cnpj_string)))
    if len(cleaned_string) == 11:
        return format_cpf_logic(cleaned_string)
    if len(cleaned_string) == 14:
        return format_cnpj_logic(cleaned_string)
    raise ValueError(
        tr("Invalid number. Pass a numeric string as the input parameter..")
    )


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def format_cpf_cnpj(cpf_cnpj_string, feature, parent):
    """
    Returns a formatted string for CPF (Brazilian individual taxpayer ID) or CNPJ (Brazilian corporate taxpayer ID).
    <br><br>Note: This function does not verify the validity of the provided number.
    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">format_cpf_cnpj</b> (<i style="color:#bf0c0c;">string</i>)</p>
    <h4>Arguments</h4>
    <p><i style="color:#bf0c0c;">string</i>: 11 or 14-numeric character string.</p>
    <h4>Example:</h4>
    <ul>
      <li> format_cpf_cnpj('00000000000') -> 000.000.000-00</li>
      <li> format_cpf_cnpj('00000000000000') -> 00.000.000/0000-00</li>
      <li> format_cpf_cnpj('000,000,000-00') -> 000.000.000-00</li>
      <li> format_cpf_cnpj('BR00,000,000/0000-00') -> 00.000.000/0000-00</li>
    </ul>
    """
    return format_cpf_cnpj_logic(cpf_cnpj_string)
