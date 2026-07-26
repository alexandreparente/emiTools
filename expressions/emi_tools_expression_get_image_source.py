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

from ._sensor_data import get_satellite_logic


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def get_image_source(filename, feature, parent):
    """
    Returns the satellite image source based on the file name.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">get_image_source</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Argument</h4>
    <p><i style="color:#bf0c0c;">string</i>: The file name of the satellite image.</p>

    <h4>Example</h4>
    <p>get_image_source('LC08_L1TP_216065_20210206_20210305_01_T1') -> 'United States Geological Survey (USGS).'</p>
    <p>get_image_source('S2A_MSIL1C_20170105T013442_N0204_R031_T53NMJ_20170105T013443') -> 'European Union\'s Earth Observation Programme (COPERNICUS).'</p>
    """
    info = get_satellite_logic(filename)
    if info:
        return info["source"]
    raise Exception("Image source could not be determined from the filename.")
