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

from qgis.PyQt.QtCore import QDate
from qgis.utils import qgsfunction

from ._sensor_data import get_image_date_logic


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def get_image_date(filename, feature, parent):
    """
    Returns the date of the satellite image based on the provided file name, following the compact naming convention of the filename.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">get_image_date</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Argument</h4>
    <p><i style="color:#bf0c0c;">String</i>: The file name of the Landsat or Sentinel image.</p>

    <h4>Example</h4>
    <p>get_image_date('LC08_L1TP_216065_20210206_20210305_01_T1') -> QDate('2021-02-06')</p>
    <p>get_image_date('S2A_MSIL1C_20170105T013442_N0204_R031_T53NMJ_20170105T013443') -> QDate('2017-01-05')</p>
    """
    d = get_image_date_logic(filename)
    return QDate(d.year, d.month, d.day)
