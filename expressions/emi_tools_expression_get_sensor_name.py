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

from ._sensor_data import get_sensor_logic


@qgsfunction(
    args="auto",
    group="EMI Tools",
    register=True,
    usesgeometry=False,
    referenced_columns=[],
)
def get_sensor_name(filename, feature, parent):
    """
    Returns the sensor name based on the provided file name.
    Supports satellite imagery and RPA (drone) imagery following the
    <tt>RPA_&lt;MODEL&gt;_&lt;SENSOR&gt;_&lt;YYYYMMDD&gt;</tt> naming convention.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">get_sensor_name</b> (<i style="color:#bf0c0c;">string</i>)</p>

    <h4>Argument</h4>
    <p><i style="color:#bf0c0c;">string</i>: The file name of the image.</p>

    <h4>RPA model codes</h4>
    <table>
      <tr><td><b>M2EA</b></td><td>DJI Mavic 2 Enterprise Advanced</td></tr>
      <tr><td><b>M3E</b></td><td>DJI Mavic 3 Enterprise</td></tr>
      <tr><td><b>M3T</b></td><td>DJI Mavic 3 Thermal</td></tr>
      <tr><td><b>M3M</b></td><td>DJI Mavic 3 Multispectral</td></tr>
      <tr><td><b>P4MS</b></td><td>DJI Phantom 4 Multispectral</td></tr>
      <tr><td><b>P4R</b></td><td>DJI Phantom 4 RTK</td></tr>
      <tr><td><b>M300</b></td><td>DJI Matrice 300 RTK</td></tr>
      <tr><td><b>M350</b></td><td>DJI Matrice 350 RTK</td></tr>
    </table>

    <h4>RPA sensor codes</h4>
    <table>
      <tr><td><b>V</b></td><td>Visível (RGB)</td></tr>
      <tr><td><b>T</b></td><td>Termal</td></tr>
      <tr><td><b>M</b></td><td>Multiespectral</td></tr>
      <tr><td><b>L</b></td><td>LiDAR</td></tr>
      <tr><td><b>H</b></td><td>Hiperespectral</td></tr>
    </table>

    <h4>Examples</h4>
    <p>get_sensor_name('LC08_L1TP_216065_20210206_20210305_01_T1') -> 'LandSat 8'</p>
    <p>get_sensor_name('S2A_MSIL1C_20170105T013442_N0204_R031_T53NMJ_20170105T013443') -> 'Sentinel 2'</p>
    <p>get_sensor_name('RPA_M2EA_V_20240315') -> 'DJI Mavic 2 Enterprise Advanced (Visível)'</p>
    <p>get_sensor_name('RPA_M2EA_T_20240315') -> 'DJI Mavic 2 Enterprise Advanced (Termal)'</p>
    <p>get_sensor_name('RPA_M300_L_20240315') -> 'DJI Matrice 300 RTK (LiDAR)'</p>
    """
    info = get_sensor_logic(filename)
    if info:
        return info["name"]
    raise Exception("Sensor name could not be determined from the filename.")
